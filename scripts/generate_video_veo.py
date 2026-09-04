"""(FALLBACK — the default Google video model is now Omni: scripts/generate_video_omni.py)
Generate a single video clip using Veo 3.1.

Usage:
    # Text-to-video
    python scripts/generate_video.py --prompt "A cat walks across a field" --output cat.mp4

    # Image-to-video (storyboard still as first frame)
    python scripts/generate_video.py --prompt "Camera dollies in..." --image scene_01.png --output scene_01.mp4

    # First + last frame interpolation (controlled transition)
    python scripts/generate_video.py --prompt "Bird spreads wings" --image start.png --last-frame end.png --output scene.mp4

    # Full model (required for first+last frame, extensions, refs)
    python scripts/generate_video.py --prompt "..." --image s.png --last-frame e.png --model full --output scene.mp4

    # Custom duration and resolution
    python scripts/generate_video.py --prompt "..." --output clip.mp4 --duration 8 --resolution 1080p
"""
import os, sys, time, argparse

MODELS = {
    "lite": "veo-3.1-lite-generate-preview",
    "full": "veo-3.1-generate-preview",
}

def main():
    parser = argparse.ArgumentParser(description="Generate video with Veo 3.1")
    parser.add_argument("--prompt", required=True, help="Video generation prompt")
    parser.add_argument("--output", required=True, help="Output file path (.mp4)")
    parser.add_argument("--image", default=None, help="First frame / storyboard image")
    parser.add_argument("--last-frame", default=None, help="Last frame for interpolation (requires --model full)")
    parser.add_argument("--model", default="lite", choices=["lite", "full"], help="Model: lite (fast/cheap) or full (interpolation/refs)")
    parser.add_argument("--duration", type=int, default=8, choices=[4, 5, 6, 8], help="Duration in seconds")
    parser.add_argument("--resolution", default="720p", choices=["720p", "1080p", "4k"], help="Output resolution")
    parser.add_argument("--aspect", default="16:9", choices=["16:9", "9:16"], help="Aspect ratio")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if output already exists")
    parser.add_argument("--poll-interval", type=int, default=10, help="Polling interval in seconds")
    args = parser.parse_args()

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return

    # Validate: last-frame requires full model
    if args.last_frame:
        if args.model != "full":
            print("WARNING: --last-frame requires full model. Switching to full.")
            args.model = "full"
        if args.duration != 8:
            print("WARNING: first+last frame interpolation requires duration=8. Setting to 8.")
            args.duration = 8

    from google import genai
    from google.genai import types

    client = genai.Client(
        http_options={"api_version": "v1beta"},
        api_key=os.environ["GEMINI_API_KEY"],
    )

    model_id = MODELS[args.model]

    # Build source
    source_kwargs = {"prompt": args.prompt}
    if args.image:
        source_kwargs["image"] = types.Image.from_file(location=args.image)

    # Build config
    config_kwargs = {
        "person_generation": "allow_adult",
        "aspect_ratio": args.aspect,
        "number_of_videos": 1,
        "duration_seconds": args.duration,
        "resolution": args.resolution,
    }
    if args.last_frame:
        config_kwargs["last_frame"] = types.Image.from_file(location=args.last_frame)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    try:
        method = "first+last frame" if args.last_frame else ("image-to-video" if args.image else "text-to-video")
        print(f"Submitting {method} | model={args.model} | {args.duration}s {args.resolution}...")

        operation = client.models.generate_videos(
            model=model_id,
            source=types.GenerateVideosSource(**source_kwargs),
            config=types.GenerateVideosConfig(**config_kwargs),
        )

        # Poll until done
        poll_count = 0
        while not operation.done:
            poll_count += 1
            elapsed = poll_count * args.poll_interval
            if poll_count % 6 == 0:
                print(f"  Processing... ({elapsed}s)")
            time.sleep(args.poll_interval)
            operation = client.operations.get(operation)

        # Save result
        if operation.result and operation.result.generated_videos:
            for gv in operation.result.generated_videos:
                client.files.download(file=gv.video)
                gv.video.save(args.output)
                print(f"SAVED {args.output}")
                return
        else:
            print("No video returned")
            if hasattr(operation, "error") and operation.error:
                print(f"Error: {operation.error}")
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

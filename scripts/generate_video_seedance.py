"""Generate video using Seedance 2.5 / 2.0 via BytePlus Ark direct API.

Endpoint: https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks

Usage:
    # Image-to-video (image must be a fetchable URL; local files auto-upload to S3)
    python scripts/generate_video_seedance.py --prompt "..." --image scene.png --output clip.mp4

    # Text-to-video (no image)
    python scripts/generate_video_seedance.py --prompt "..." --output clip.mp4

    # Multiple reference images (up to 9)
    python scripts/generate_video_seedance.py --prompt "..." \
        --image img1.png --image img2.png --output clip.mp4

    # Reference video (for camera/motion replication)
    python scripts/generate_video_seedance.py --prompt "..." \
        --image img1.png --ref-video ref.mp4 --output clip.mp4

    # Reference audio (for BGM matching)
    python scripts/generate_video_seedance.py --prompt "..." \
        --image img1.png --ref-audio bgm.mp3 --output clip.mp4

    # Fast model (cheaper, quicker drafts)
    python scripts/generate_video_seedance.py --prompt "..." \
        --image scene.png --output clip.mp4 --model fast

    # Seedance 2.5: 30s one-shot ad with a still + several motion/camera reference videos
    python scripts/generate_video_seedance.py --model 2.5 --duration 30 --prompt "... refer to @Image1 ... camera like @Video1 ..." \
        --image product.png --ref-video move_a.mp4 --ref-video move_b.mp4 --task-type reference --output ad.mp4

    # Seedance 2.5: first + last frame (ratio auto = adaptive)
    python scripts/generate_video_seedance.py --model 2.5 --prompt "..." \
        --first-frame start.png --last-frame end.png --duration 8 --output clip.mp4

    # Seedance 2.5: edit / extend an existing clip (4-30s source; prompt must say edit/remove/replace or extend/continue)
    python scripts/generate_video_seedance.py --model 2.5 --task-type edit --prompt "Video edit: remove the person in @Video1" \
        --ref-video clip.mp4 --output clip_edit.mov --output-format mov
    python scripts/generate_video_seedance.py --model 2.5 --task-type extend --duration 10 --prompt "Extend @Video1 forward: ..." \
        --ref-video clip.mp4 --output clip_ext.mp4

    # Custom duration/ratio
    python scripts/generate_video_seedance.py --prompt "..." \
        --image scene.png --output clip.mp4 --duration 10 --ratio 9:16

Requires:
    ARK_API_KEY in environment (BytePlus Ark)
    S3_BUCKET (+ S3_REGION, optional S3_PUBLIC_URL) for auto-upload of local files; see scripts/media_host.py
"""
import os, sys, argparse, json, time, urllib.request


def upload_to_host(local_path, prefix="seedance"):
    """Upload a local file to the configured host (S3 default, R2 legacy) and return a fetchable URL."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from media_host import upload_public
    return upload_public(local_path, prefix)


def resolve_url(local_path, url, label="file", prefix="seedance"):
    """Return url if provided, else upload local_path to R2 and return its URL."""
    if url:
        return url
    if not local_path:
        return None
    print(f"Uploading {label} {local_path} to S3...")
    result = upload_to_host(local_path, prefix)
    if not result:
        print(f"ERROR: Could not upload {label}. Set S3_BUCKET (+S3_REGION) or use a URL flag.")
        sys.exit(1)
    print(f"  -> {result}")
    return result


ARK_BASE = "https://ark.ap-southeast.bytepluses.com/api/v3"
MODELS = {
    "2.5":  "dreamina-seedance-2-5-260628",       # up to 30s, 50 refs (30 img + 10 vid + 10 audio), edit/extend, mov output
    "full": "dreamina-seedance-2-0-260128",       # Seedance 2.0 quality, up to 15s, 4K
    "fast": "dreamina-seedance-2-0-fast-260128",  # drafts
    "mini": "dreamina-seedance-2-0-mini-260615",  # cheapest, 720p max
}
# Per-model reference limits (images, videos, audios, max duration seconds)
LIMITS = {
    "2.5":  (30, 10, 10, 30),
    "full": (9, 3, 3, 15),
    "fast": (9, 3, 3, 15),
    "mini": (9, 3, 3, 15),
}


def ark_request(method, path, api_key, body=None):
    """Minimal HTTP helper for Ark API using urllib (no extra deps)."""
    url = f"{ARK_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = ""
        raise RuntimeError(f"Ark HTTP {e.code}: {err_body}") from e


def main():
    parser = argparse.ArgumentParser(
        description="Seedance 2.0 via BytePlus Ark direct API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt", required=True, help="Video generation prompt")
    parser.add_argument("--output", required=True, help="Output file path (.mp4)")
    parser.add_argument("--model", default="full", choices=list(MODELS.keys()),
                        help="2.5 = Seedance 2.5 (30s, 50 refs, edit/extend); full = Seedance 2.0 (quality); "
                             "fast = 2.0 fast (drafts); mini = 2.0 mini (cheapest)")
    parser.add_argument("--image", action="append", default=[],
                        help="Local reference image (repeatable, up to 9; first is the opening frame)")
    parser.add_argument("--image-url", action="append", default=[],
                        help="Hosted reference image URL (repeatable)")
    parser.add_argument("--first-frame", default=None, help="Local image used as FIRST frame (role=first_frame; ratio forced to adaptive)")
    parser.add_argument("--first-frame-url", default=None, help="Hosted first-frame image URL")
    parser.add_argument("--last-frame", default=None, help="Local image used as LAST frame (role=last_frame; needs --first-frame)")
    parser.add_argument("--last-frame-url", default=None, help="Hosted last-frame image URL")
    parser.add_argument("--ref-video", action="append", default=[], help="Local reference video file (repeatable; 2.5: up to 10)")
    parser.add_argument("--ref-video-url", action="append", default=[], help="Hosted reference video URL (repeatable)")
    parser.add_argument("--ref-audio", action="append", default=[], help="Local reference audio file (repeatable; 2.5: up to 10)")
    parser.add_argument("--ref-audio-url", action="append", default=[], help="Hosted reference audio URL (repeatable)")
    parser.add_argument("--task-type", default=None, choices=["auto", "reference", "edit", "extend"],
                        help="omni_reference_task_type (Seedance 2.5): reference | edit (ratio=adaptive, duration=-1) | extend | auto")
    parser.add_argument("--output-format", default=None, choices=["mp4", "mov"],
                        help="Seedance 2.5 only: mov = H.264 yuv444p + PCM (better color fidelity for edit/extend)")
    parser.add_argument("--duration", type=int, default=8,  # -1 = model picks (2.5 supports 4-30s, 2.0 series 4-15s)
                        help="Duration in seconds (default: 8)")
    parser.add_argument("--ratio", default="16:9",  # 21:9 16:9 4:3 1:1 3:4 9:16 adaptive
                        help="Aspect ratio: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 (default: 16:9)")
    parser.add_argument("--generate-audio", action="store_true", default=True,
                        help="Generate synchronized audio (default: on)")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio generation")
    parser.add_argument("--watermark", action="store_true", default=False,
                        help="Include BytePlus watermark (default: off)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--poll-interval", type=float, default=5.0,
                        help="Seconds between status polls (default: 5)")
    parser.add_argument("--timeout", type=int, default=900,
                        help="Max seconds to wait for completion (default: 900)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if output exists")
    args = parser.parse_args()

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return

    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("ERROR: ARK_API_KEY not set. Run: source config.env")
        sys.exit(1)

    # Resolve all reference URLs
    image_urls = list(args.image_url)
    for img in args.image:
        url = resolve_url(img, None, "image")
        if url:
            image_urls.append(url)
    video_urls = list(args.ref_video_url) + [u for u in (resolve_url(v, None, "reference video") for v in args.ref_video) if u]
    audio_urls = list(args.ref_audio_url) + [u for u in (resolve_url(a, None, "reference audio") for a in args.ref_audio) if u]
    first_url = resolve_url(args.first_frame, args.first_frame_url, "first frame")
    last_url = resolve_url(args.last_frame, args.last_frame_url, "last frame")

    max_img, max_vid, max_aud, max_dur = LIMITS[args.model]
    if len(image_urls) > max_img:
        print(f"ERROR: Max {max_img} reference images for model {args.model} (got {len(image_urls)}).")
        sys.exit(1)
    if len(video_urls) > max_vid or len(audio_urls) > max_aud:
        print(f"ERROR: Max {max_vid} reference videos / {max_aud} audios for model {args.model}.")
        sys.exit(1)
    if args.duration != -1 and not (4 <= args.duration <= max_dur):
        print(f"ERROR: duration must be 4-{max_dur}s (or -1 = auto) for model {args.model}.")
        sys.exit(1)
    if last_url and not first_url:
        print("ERROR: --last-frame requires --first-frame.")
        sys.exit(1)

    # Build content array
    content = [{"type": "text", "text": args.prompt}]
    if first_url:
        content.append({"type": "image_url", "image_url": {"url": first_url}, "role": "first_frame"})
    if last_url:
        content.append({"type": "image_url", "image_url": {"url": last_url}, "role": "last_frame"})
    for url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": url}, "role": "reference_image"})
    for url in video_urls:
        content.append({"type": "video_url", "video_url": {"url": url}, "role": "reference_video"})
    for url in audio_urls:
        content.append({"type": "audio_url", "audio_url": {"url": url}, "role": "reference_audio"})

    ratio = args.ratio
    duration = args.duration
    # Seedance constraints: first/last-frame and edit/extend tasks require ratio=adaptive; edit requires duration=-1
    if first_url and ratio != "adaptive":
        print("NOTE: first-frame task -> ratio forced to 'adaptive' (output keeps the first frame's aspect).")
        ratio = "adaptive"
    if args.task_type in ("edit", "extend") and ratio != "adaptive":
        print(f"NOTE: {args.task_type} task -> ratio forced to 'adaptive'.")
        ratio = "adaptive"
    if args.task_type == "edit" and duration != -1:
        print("NOTE: edit task -> duration forced to -1 (keeps source duration).")
        duration = -1

    body = {
        "model": MODELS[args.model],
        "content": content,
        "generate_audio": (not args.no_audio) and args.generate_audio,
        "ratio": ratio,
        "duration": duration,
        "watermark": args.watermark,
    }
    if args.task_type:
        body["omni_reference_task_type"] = args.task_type
    if args.output_format:
        if args.model != "2.5" and args.output_format == "mov":
            print("WARNING: mov output is Seedance 2.5 only; ignoring for", args.model)
        else:
            body["output_format"] = args.output_format
    if args.seed is not None:
        body["seed"] = args.seed

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    # Submit task
    print(f"Submitting Seedance | model={args.model} ({MODELS[args.model]}) | {duration}s | ratio={ratio}")
    print(f"  Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    if image_urls:
        print(f"  Images: {len(image_urls)} reference(s)")
    if first_url:
        print(f"  First frame: {first_url}" + (f" -> last frame: {last_url}" if last_url else ""))
    for v in video_urls:
        print(f"  Ref video: {v}")
    for a in audio_urls:
        print(f"  Ref audio: {a}")

    try:
        submit = ark_request("POST", "/contents/generations/tasks", api_key, body)
    except RuntimeError as e:
        print(f"ERROR submitting task: {e}")
        sys.exit(1)

    task_id = submit.get("id") or submit.get("task_id")
    if not task_id:
        print(f"ERROR: No task id in response:\n{json.dumps(submit, indent=2)}")
        sys.exit(1)

    print(f"Task ID: {task_id}")
    print(f"Polling every {args.poll_interval}s (timeout {args.timeout}s)...")

    # Poll for completion
    start = time.time()
    last_status = None
    while True:
        elapsed = time.time() - start
        if elapsed > args.timeout:
            print(f"\nERROR: Timeout after {args.timeout}s. Task {task_id} still pending.")
            sys.exit(1)
        try:
            status_resp = ark_request("GET", f"/contents/generations/tasks/{task_id}", api_key)
        except RuntimeError as e:
            print(f"\nERROR polling: {e}")
            sys.exit(1)

        status = status_resp.get("status", "unknown")
        if status != last_status:
            print(f"  [{int(elapsed)}s] status={status}")
            last_status = status

        if status in ("succeeded", "success", "completed"):
            # Extract video URL from response
            dl_url = None
            cnt = status_resp.get("content") or {}
            if isinstance(cnt, dict):
                dl_url = cnt.get("video_url") or cnt.get("url")
            if not dl_url:
                # some responses nest under "result" / "output"
                for key in ("result", "output", "data"):
                    val = status_resp.get(key) or {}
                    if isinstance(val, dict):
                        dl_url = val.get("video_url") or val.get("url")
                        if dl_url:
                            break
            if not dl_url:
                print(f"ERROR: Task succeeded but no video URL found:\n{json.dumps(status_resp, indent=2)}")
                sys.exit(1)

            print(f"Downloading video from {dl_url[:80]}...")
            urllib.request.urlretrieve(dl_url, args.output)
            size_mb = os.path.getsize(args.output) / (1024 * 1024)
            print(f"SAVED {args.output} ({size_mb:.1f} MB)")
            return

        if status in ("failed", "error", "cancelled"):
            err = status_resp.get("error") or status_resp.get("message") or status_resp
            print(f"\nTASK FAILED: {json.dumps(err, indent=2) if isinstance(err, dict) else err}")
            # Content policy hint
            err_str = json.dumps(status_resp).lower()
            if "policy" in err_str or "likeness" in err_str or "unsafe" in err_str:
                print("\nLikely content policy block. Workarounds:")
                print("  1. Use 3D/Pixar-style characters instead of photorealistic faces")
                print("  2. Use product-only shots")
                print("  3. Switch to LTX: python scripts/generate_video_ltx.py ...")
            sys.exit(1)

        time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()

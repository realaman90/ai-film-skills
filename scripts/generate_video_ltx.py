"""Generate video using LTX 2.3 via direct LTX API (docs.ltx.video).

Endpoints (all POST, base URL https://api.ltx.video/v1):
    /text-to-video       text -> video
    /image-to-video      image + text -> video
    /audio-to-video      audio + image/text -> video
    /extend              extend existing video forward/backward
    /retake              retake a section of existing video
    /upload              get pre-signed upload URL for local files

All generation endpoints return the finished video directly as a binary stream
(application/octet-stream) in the 200 response -- no polling required.

Usage:
    # Image-to-video (fast model, default)
    python scripts/generate_video_ltx.py --prompt "..." --image scene.png --output clip.mp4

    # Image-to-video (pro quality)
    python scripts/generate_video_ltx.py --prompt "..." --image scene.png --output clip.mp4 \
        --endpoint image-to-video --ltx-model ltx-2-3-pro

    # Text-to-video
    python scripts/generate_video_ltx.py --prompt "..." --output clip.mp4 --endpoint text-to-video

    # End frame interpolation (ltx-2-3 / ltx-2-5)
    python scripts/generate_video_ltx.py --prompt "..." --image start.png --end-image end.png \
        --output clip.mp4

    # Extend existing video
    python scripts/generate_video_ltx.py --prompt "She turns the corner" --video clip.mp4 \
        --output extended.mp4 --endpoint extend --duration 5 --extend-mode end

    # Retake a section
    python scripts/generate_video_ltx.py --prompt "She smiles warmly" --video clip.mp4 \
        --output fixed.mp4 --endpoint retake --start-time 2 --duration 3

    # Audio-to-video
    python scripts/generate_video_ltx.py --prompt "Woman dancing" --audio music.mp3 \
        --image dancer.png --output mv.mp4 --endpoint audio-to-video

    # Longer clip
    python scripts/generate_video_ltx.py --prompt "..." --image scene.png --output clip.mp4 \
        --duration 15

    # With hosted URL (already on the internet)
    python scripts/generate_video_ltx.py --prompt "..." --image-url https://... --output clip.mp4

Requires:
    LTXV_API_KEY in environment (from config.env)
"""
import os, sys, argparse, json, time, urllib.request, urllib.parse

LTX_BASE = "https://api.ltx.video/v1"

# Our friendly endpoint names -> LTX API paths
ENDPOINTS = {
    "image-to-video": "/image-to-video",
    "text-to-video":  "/text-to-video",
    "audio-to-video": "/audio-to-video",
    "extend":         "/extend",
    "retake":         "/retake",
}

# Model names supported by LTX API (ltx-2-fast / ltx-2-pro were retired 2026-08-15)
#   ltx-2-3-fast / ltx-2-3-pro : t2v, i2v, last-frame; PRO also extend / retake / audio-to-video. 2-20s.
#   ltx-2-5-fast / ltx-2-5-pro : newest look (Aug 2026), t2v, i2v, audio-to-video, last-frame, camera_motion.
#                                6-20s (fast, up to 4K) / 6-10s (pro, up to 1080p). NO extend / retake -> use ltx-2-3-pro.
LTX_MODELS = ["ltx-2-3-fast", "ltx-2-3-pro", "ltx-2-5-fast", "ltx-2-5-pro"]
EXTEND_RETAKE_MODELS = ("ltx-2-3-pro",)


def upload_local_to_ltx(local_path, api_key):
    """Use LTX's /upload endpoint to get a pre-signed URL, PUT the file, return the storage_uri."""
    req = urllib.request.Request(
        f"{LTX_BASE}/upload",
        method="POST",
        data=b"",
    )
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            info = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LTX /upload failed {e.code}: {err}") from e

    upload_url = info.get("upload_url")
    storage_uri = info.get("storage_uri")
    required_headers = info.get("required_headers") or {}
    if not upload_url or not storage_uri:
        raise RuntimeError(f"LTX /upload missing fields: {info}")

    with open(local_path, "rb") as f:
        data = f.read()
    put_req = urllib.request.Request(upload_url, data=data, method="PUT")
    for k, v in required_headers.items():
        put_req.add_header(k, v)
    if "Content-Type" not in required_headers:
        ext = os.path.splitext(local_path)[1].lower()
        content_types = {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".mp4": "video/mp4", ".mov": "video/quicktime",
            ".mp3": "audio/mpeg", ".wav": "audio/wav",
        }
        put_req.add_header("Content-Type", content_types.get(ext, "application/octet-stream"))
    try:
        with urllib.request.urlopen(put_req, timeout=300) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PUT upload failed {e.code}: {err}") from e

    return storage_uri


def resolve_uri(local_path, url, api_key, label="file"):
    """Return url if provided, else upload local_path via LTX /upload and return its storage_uri."""
    if url:
        return url
    if not local_path:
        return None
    print(f"Uploading {label} {local_path} to LTX...")
    uri = upload_local_to_ltx(local_path, api_key)
    print(f"  -> {uri}")
    return uri


def post_and_save(path, body, api_key, output_path):
    """POST JSON body to LTX API and stream the binary response to output_path."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{LTX_BASE}{path}", data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    print(f"POST {path}")
    print(f"  Body: {json.dumps({k: v for k, v in body.items() if k != 'prompt'})}")
    print(f"  Prompt: {str(body.get('prompt', ''))[:100]}{'...' if len(str(body.get('prompt', ''))) > 100 else ''}")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=1800) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "json" in content_type.lower():
                # Error or async task
                info = json.loads(resp.read().decode("utf-8"))
                raise RuntimeError(f"Expected video, got JSON: {info}")
            with open(output_path, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 256)
                    if not chunk:
                        break
                    f.write(chunk)
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LTX {path} failed {e.code}: {err}") from e
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"SAVED {output_path} ({size_mb:.1f} MB in {time.time() - t0:.1f}s)")


def main():
    parser = argparse.ArgumentParser(
        description="LTX 2.3 video generation via direct LTX API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt", default=None, help="Video generation prompt")
    parser.add_argument("--output", required=True, help="Output file path (.mp4)")
    parser.add_argument("--endpoint", default="image-to-video", choices=list(ENDPOINTS.keys()),
                        help="Which LTX endpoint to call (default: image-to-video)")
    parser.add_argument("--ltx-model", default="ltx-2-3-fast", choices=LTX_MODELS,
                        help="LTX model variant (default: ltx-2-3-fast)")
    parser.add_argument("--duration", type=int, default=6,
                        help="Duration in seconds (default: 6)")
    parser.add_argument("--resolution", default="1920x1080",
                        help="Output resolution (e.g. 1920x1080, 1080x1920, 3840x2160)")
    parser.add_argument("--fps", type=int, default=None, help="Frames per second (default: model default)")
    parser.add_argument("--generate-audio", action="store_true", default=True,
                        help="Generate synchronized audio (default: on)")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio generation")
    parser.add_argument("--camera-motion", default=None,
                        choices=["dolly_in", "dolly_out", "dolly_left", "dolly_right",
                                 "jib_up", "jib_down", "static", "focus_shift"],
                        help="Predefined camera motion")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if output exists")

    # Image inputs
    parser.add_argument("--image", default=None, help="Local image (auto-uploaded)")
    parser.add_argument("--image-url", default=None, help="Image URL or storage_uri (already hosted)")
    parser.add_argument("--end-image", default=None, help="Local end image (last_frame_uri; ltx-2-3 / ltx-2-5)")
    parser.add_argument("--end-image-url", default=None, help="End image URL or storage_uri")

    # Video inputs (for extend/retake)
    parser.add_argument("--video", default=None, help="Local video (auto-uploaded)")
    parser.add_argument("--video-url", default=None, help="Video URL or storage_uri")

    # Audio inputs (for audio-to-video)
    parser.add_argument("--audio", default=None, help="Local audio (auto-uploaded)")
    parser.add_argument("--audio-url", default=None, help="Audio URL or storage_uri")

    # Extend-specific
    parser.add_argument("--extend-mode", default="end", choices=["start", "end"],
                        help="Extend at start or end (default: end)")
    parser.add_argument("--context", type=float, default=None,
                        help="Seconds of input video to use as context (extend)")

    # Retake-specific
    parser.add_argument("--start-time", type=float, default=None,
                        help="Retake start position in seconds")
    parser.add_argument("--retake-mode", default="replace_audio_and_video",
                        choices=["replace_audio", "replace_video", "replace_audio_and_video"],
                        help="Retake mode (default: replace_audio_and_video)")

    # Audio-to-video specific
    parser.add_argument("--guidance-scale", type=float, default=None,
                        help="CFG guidance scale (audio-to-video)")

    args = parser.parse_args()

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return

    api_key = os.environ.get("LTXV_API_KEY")
    if not api_key:
        print("ERROR: LTXV_API_KEY not set. Run: source config.env")
        sys.exit(1)

    ep = args.endpoint
    path = ENDPOINTS[ep]

    # Resolve URIs (upload local files as needed)
    image_uri = resolve_uri(args.image, args.image_url, api_key, "image")
    end_image_uri = resolve_uri(args.end_image, args.end_image_url, api_key, "end image")
    video_uri = resolve_uri(args.video, args.video_url, api_key, "video")
    audio_uri = resolve_uri(args.audio, args.audio_url, api_key, "audio")

    # Validate per endpoint
    if ep == "image-to-video" and not image_uri:
        print("ERROR: image-to-video requires --image or --image-url.")
        sys.exit(1)
    if ep == "text-to-video" and not args.prompt:
        print("ERROR: text-to-video requires --prompt.")
        sys.exit(1)
    if ep == "extend" and not video_uri:
        print("ERROR: extend requires --video or --video-url.")
        sys.exit(1)
    if ep == "retake" and not video_uri:
        print("ERROR: retake requires --video or --video-url.")
        sys.exit(1)
    if ep == "retake" and args.start_time is None:
        print("ERROR: retake requires --start-time.")
        sys.exit(1)
    if ep == "audio-to-video" and not audio_uri:
        print("ERROR: audio-to-video requires --audio or --audio-url.")
        sys.exit(1)
    if ep == "audio-to-video" and not image_uri and not args.prompt:
        print("ERROR: audio-to-video requires at least --prompt or --image.")
        sys.exit(1)

    # Build body per endpoint
    body = {}
    gen_audio = (not args.no_audio) and args.generate_audio

    if ep in ("image-to-video", "text-to-video"):
        body["model"] = args.ltx_model
        body["prompt"] = args.prompt
        body["duration"] = args.duration
        body["resolution"] = args.resolution
        if args.fps is not None:
            body["fps"] = args.fps
        if not gen_audio:
            body["generate_audio"] = False
        if args.camera_motion:
            body["camera_motion"] = args.camera_motion
        if ep == "image-to-video":
            body["image_uri"] = image_uri
            if end_image_uri:
                body["last_frame_uri"] = end_image_uri

    elif ep == "extend":
        # Extend is supported by ltx-2-3-pro only (2.5 family has no extend/retake)
        model = args.ltx_model if args.ltx_model in EXTEND_RETAKE_MODELS else "ltx-2-3-pro"
        if model != args.ltx_model:
            print(f"NOTE: {args.ltx_model} does not support extend -> using {model}")
        body["model"] = model
        body["video_uri"] = video_uri
        body["duration"] = args.duration
        body["mode"] = args.extend_mode
        if args.prompt:
            body["prompt"] = args.prompt
        if args.context is not None:
            body["context"] = args.context

    elif ep == "retake":
        model = args.ltx_model if args.ltx_model in EXTEND_RETAKE_MODELS else "ltx-2-3-pro"
        if model != args.ltx_model:
            print(f"NOTE: {args.ltx_model} does not support retake -> using {model}")
        body["model"] = model
        body["video_uri"] = video_uri
        body["start_time"] = args.start_time
        body["duration"] = args.duration
        body["mode"] = args.retake_mode
        if args.prompt:
            body["prompt"] = args.prompt
        if args.resolution in ("1920x1080", "1080x1920"):
            body["resolution"] = args.resolution

    elif ep == "audio-to-video":
        body["model"] = args.ltx_model if args.ltx_model.startswith(("ltx-2-3", "ltx-2-5")) else "ltx-2-3-pro"
        body["audio_uri"] = audio_uri
        if image_uri:
            body["image_uri"] = image_uri
        if args.prompt:
            body["prompt"] = args.prompt
        if args.resolution in ("1920x1080", "1080x1920"):
            body["resolution"] = args.resolution
        if args.guidance_scale is not None:
            body["guidance_scale"] = args.guidance_scale

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    try:
        post_and_save(path, body, api_key, args.output)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

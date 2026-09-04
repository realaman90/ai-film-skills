#!/usr/bin/env python3
"""Generate video with Google Gemini Omni (gemini-omni-1.1-flash) via the Interactions REST API.

Replaces Veo 3.1 as the default Google video model (Sept 2026). Talks REST directly (urllib) so it works
on any Python; the Interactions API needs google-genai >= 2.x / Python 3.10+ if you use the SDK instead.

Capabilities (3-10 s per generation, 24 fps, native 720p; 1080p/4K are upscales; extension chains to 40 s):
    text-to-video, image-to-video (first frame), first + last frame, subject/reference images (@IMAGE_REF_n),
    reference video clips (<=3 clips, <=3 s each), edit an uploaded video (<=10 s), extend a video (+3-10 s),
    multi-turn edits via --previous, 360p draft -> upscale to 1080p/4K via --upscale.

Usage:
    source ~/config.env   # GEMINI_API_KEY

    # Image-to-video (storyboard still as first frame) — most common
    python scripts/generate_video_omni.py --prompt "Slow dolly forward. Ambient: crickets." --image scene.png --output clip.mp4

    # Text-to-video, portrait, 1080p
    python scripts/generate_video_omni.py --prompt "..." --ratio 9:16 --resolution 1080p --output clip.mp4

    # First + last frame
    python scripts/generate_video_omni.py --prompt "Wings unfold, lifts off" --image start.png --last-frame end.png --output clip.mp4

    # Subject references (character sheet + prop), not used as first frame
    python scripts/generate_video_omni.py --prompt "The character in <IMAGE_REF_0> picks up the bottle in <IMAGE_REF_1>" \
        --ref char.png --ref bottle.png --output clip.mp4

    # Cheap draft at 360p, then upscale the result you like
    python scripts/generate_video_omni.py --prompt "..." --image s.png --resolution 360p --output draft.mp4
    python scripts/generate_video_omni.py --upscale draft.mp4 --resolution 4k --output final_4k.mp4

    # Extend an existing clip (must be <=10 s; appends 3-10 s; chain up to 40 s total)
    python scripts/generate_video_omni.py --extend clip.mp4 --prompt "Continue the scene: she turns and walks out" --output clip_ext.mp4

    # Edit an existing clip
    python scripts/generate_video_omni.py --edit clip.mp4 --prompt "Make the sky overcast, remove the car" --output clip_v2.mp4

    # Multi-turn: refine the previous generation (id printed by the previous run / saved in <output>.json)
    python scripts/generate_video_omni.py --previous v1_abc123 --prompt "Make the camera move slower" --output clip_v2.mp4

Notes:
    - No explicit duration parameter: say it in the prompt ("An 8-second continuous shot ...") via --duration.
    - Every output carries an invisible SynthID watermark. Audio is generated natively.
    - Cost (Sept 2026): ~$0.03/s 360p · $0.10/s 720p · $0.15/s 1080p · $0.30/s 4K.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
MODELS = {"omni": "gemini-omni-1.1-flash", "omni-preview": "gemini-omni-flash-preview"}


def die(msg, code=1):
    print(f"ERROR: {redact(msg)}", file=sys.stderr)
    sys.exit(code)


def redact(text):
    """Never let an API key reach stdout/stderr/transcripts."""
    import re
    return re.sub(r"(key=|AIza)[A-Za-z0-9_\-]{8,}", r"\1***", str(text))


def http(method, url, body=None, timeout=900, raw=False, key=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if key:
        req.add_header("x-goog-api-key", key)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = r.read()
            return payload if raw else json.loads(payload.decode())
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode()
        except Exception:
            err = ""
        raise RuntimeError(redact(f"HTTP {e.code} {url.split('?')[0]}: {err[:800]}")) from e


def b64_file(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), mime


def upload_file(path, key):
    """Files API upload (resumable, single shot). Returns file uri after it is ACTIVE."""
    size = os.path.getsize(path)
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    start = urllib.request.Request(f"{API.replace('/v1beta', '')}/upload/v1beta/files", method="POST",
                                   data=json.dumps({"file": {"display_name": os.path.basename(path)}}).encode())
    start.add_header("X-Goog-Upload-Protocol", "resumable")
    start.add_header("X-Goog-Upload-Command", "start")
    start.add_header("X-Goog-Upload-Header-Content-Length", str(size))
    start.add_header("X-Goog-Upload-Header-Content-Type", mime)
    start.add_header("Content-Type", "application/json")
    start.add_header("x-goog-api-key", key)
    with urllib.request.urlopen(start, timeout=60) as r:
        upload_url = r.headers.get("X-Goog-Upload-URL")
    if not upload_url:
        die("Files API did not return an upload URL")
    with open(path, "rb") as f:
        data = f.read()
    fin = urllib.request.Request(upload_url, method="POST", data=data)
    fin.add_header("Content-Length", str(size))
    fin.add_header("X-Goog-Upload-Offset", "0")
    fin.add_header("X-Goog-Upload-Command", "upload, finalize")
    fin.add_header("x-goog-api-key", key)
    with urllib.request.urlopen(fin, timeout=600) as r:
        info = json.loads(r.read().decode())["file"]
    name = info["name"]
    while info.get("state") not in ("ACTIVE", "FAILED"):
        time.sleep(3)
        info = http("GET", f"{API}/{name}", key=key)
    if info.get("state") == "FAILED":
        die(f"upload of {path} failed")
    return info["uri"]


def find_video(interaction):
    """Return (b64_data_or_None, uri_or_None) from an Interactions response."""
    for step in interaction.get("steps", []) or []:
        if step.get("type") != "model_output":
            continue
        for c in step.get("content", []) or []:
            if c.get("type") == "video":
                return c.get("data"), c.get("uri")
    # some responses expose output_video directly
    ov = interaction.get("output_video") or {}
    if ov:
        return ov.get("data"), ov.get("uri")
    return None, None


def download_uri(uri, key, out_path):
    import re
    m = re.search(r"files/([A-Za-z0-9_\-]+)", uri)
    if not m:
        die(f"cannot parse file id from uri {uri}")
    file_id = f"files/{m.group(1)}"
    waited = 0
    while True:
        info = http("GET", f"{API}/{file_id}", key=key)
        if info.get("state") == "ACTIVE":
            break
        if info.get("state") == "FAILED":
            die("output file processing failed")
        time.sleep(3)
        waited += 3
        if waited % 15 == 0:
            print(f"  waiting for output file... ({waited}s)")
    data = http("GET", f"{API}/{file_id}:download?alt=media", raw=True, key=key)
    with open(out_path, "wb") as f:
        f.write(data)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prompt", default=None, help="What happens + camera + light + audio. Required unless --upscale")
    p.add_argument("--output", required=True, help="Output .mp4")
    p.add_argument("--model", default="omni", help="omni (gemini-omni-1.1-flash) | omni-preview | raw model id")
    p.add_argument("--image", default=None, help="First-frame image (image-to-video)")
    p.add_argument("--last-frame", default=None, help="Last-frame image (needs --image)")
    p.add_argument("--ref", action="append", default=[], help="Subject/style reference image (repeatable); address as <IMAGE_REF_n> in the prompt")
    p.add_argument("--ref-video", action="append", default=[], help="Reference video clip (<=3 clips, <=3 s each)")
    p.add_argument("--extend", default=None, help="Existing video (<=10 s) to extend by 3-10 s")
    p.add_argument("--edit", default=None, help="Existing video (<=10 s) to edit with the prompt")
    p.add_argument("--upscale", default=None, help="Existing (360p/720p) video to upscale to --resolution")
    p.add_argument("--previous", default=None, help="previous interaction id for multi-turn refinement")
    p.add_argument("--ratio", default="16:9", choices=["16:9", "9:16"])
    p.add_argument("--resolution", default="720p", choices=["360p", "720p", "1080p", "4k"])
    p.add_argument("--duration", type=int, default=None, help="Target seconds 3-10 (written into the prompt; no hard API control)")
    p.add_argument("--task", default=None, choices=["text_to_video", "image_to_video", "reference_to_video", "edit", "extend"],
                   help="Force the video task (auto-detected otherwise)")
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--download", default=None, help="Recover: download a finished output by files/<id> or interaction id (no generation)")
    args = p.parse_args()

    if args.download:
        key = os.environ.get("GEMINI_API_KEY") or die("GEMINI_API_KEY not set")
        target = args.download
        if "files/" not in target:
            res = http("GET", f"{API}/interactions/{target}", key=key)
            _, target = find_video(res)
            if not target:
                die("no video uri on that interaction")
        download_uri(target, key, args.output)
        print(f"SAVED {args.output}")
        return

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        die("GEMINI_API_KEY not set. Run: source ~/config.env")
    if not args.prompt and not args.upscale:
        die("--prompt is required (unless --upscale)")
    if args.last_frame and not args.image:
        die("--last-frame needs --image (the first frame)")
    if len(args.ref_video) > 3:
        die("max 3 reference videos")
    model = MODELS.get(args.model, args.model)

    prompt = args.prompt or ""
    if args.duration:
        if not 3 <= args.duration <= 10:
            die("--duration must be 3-10 s per generation (use --extend to chain up to 40 s)")
        prompt = f"A {args.duration}-second continuous shot. " + prompt

    content = []
    task = args.task
    # --- uploaded media (edit / extend / upscale / ref videos) go through the Files API
    if args.upscale:
        print(f"Uploading {args.upscale} for upscale...")
        content.append({"type": "document", "uri": upload_file(args.upscale, key)})
        prompt = prompt or f"Upscale this video to {args.resolution}. Keep every frame, motion and audio identical."
        task = task or "edit"
    if args.extend:
        print(f"Uploading {args.extend} for extension...")
        content.append({"type": "document", "uri": upload_file(args.extend, key)})
        task = task or "extend"
    if args.edit:
        print(f"Uploading {args.edit} for editing...")
        content.append({"type": "document", "uri": upload_file(args.edit, key)})
        task = task or "edit"
    for rv in args.ref_video:
        print(f"Uploading reference video {rv}...")
        content.append({"type": "document", "uri": upload_file(rv, key)})
    # --- inline images
    if args.image:
        data, mime = b64_file(args.image)
        content.append({"type": "image", "data": data, "mime_type": mime})
        task = task or "image_to_video"
    if args.last_frame:
        data, mime = b64_file(args.last_frame)
        content.append({"type": "image", "data": data, "mime_type": mime})
    for r in args.ref:
        data, mime = b64_file(r)
        content.append({"type": "image", "data": data, "mime_type": mime})
        if not args.image:
            task = task or "reference_to_video"
    content.append({"type": "text", "text": prompt})
    if not task and not args.previous:
        task = "text_to_video"

    body = {
        "model": model,
        "input": content if len(content) > 1 else prompt,
        "response_format": {"type": "video", "aspect_ratio": args.ratio, "resolution": args.resolution, "delivery": "uri"},
    }
    if task:
        body["generation_config"] = {"video_config": {"task": task}}
    if args.previous:
        body["previous_interaction_id"] = args.previous

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    print(f"Submitting Omni | model={model} | task={task or 'auto'} | {args.ratio} {args.resolution}"
          + (f" | ~{args.duration}s" if args.duration else ""))
    print(f"  Prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    t0 = time.time()
    try:
        res = http("POST", f"{API}/interactions", body, timeout=args.timeout, key=key)
    except RuntimeError as e:
        die(str(e))

    # async fallback: poll if not completed
    iid = res.get("id")
    status = res.get("status")
    while status not in (None, "completed", "failed", "cancelled") and iid:
        time.sleep(5)
        res = http("GET", f"{API}/interactions/{iid}", key=key)
        status = res.get("status")
        print(f"  [{int(time.time() - t0)}s] status={status}")
    if status == "failed":
        die(f"generation failed: {json.dumps(res)[:800]}")

    data, uri = find_video(res)
    with open(args.output + ".json", "w") as f:
        json.dump({"interaction_id": iid, "video_uri": uri, "status": status}, f, indent=2)
    if data:
        with open(args.output, "wb") as f:
            f.write(base64.b64decode(data))
    elif uri:
        download_uri(uri, key, args.output)
    else:
        die(f"no video in response: {json.dumps(res)[:1200]}")

    meta = {"interaction_id": iid, "model": model, "task": task, "ratio": args.ratio, "resolution": args.resolution,
            "prompt": prompt, "inputs": {"image": args.image, "last_frame": args.last_frame, "refs": args.ref,
                                         "ref_videos": args.ref_video, "extend": args.extend, "edit": args.edit,
                                         "upscale": args.upscale, "previous": args.previous}}
    with open(args.output + ".json", "w") as f:
        json.dump(meta, f, indent=2)
    size_mb = os.path.getsize(args.output) / 1e6
    print(f"SAVED {args.output} ({size_mb:.1f} MB) in {int(time.time() - t0)}s | interaction id: {iid}")
    print(f"  Refine with: --previous {iid}")


if __name__ == "__main__":
    main()

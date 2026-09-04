"""Generate images using BytePlus Ark Seedream 5.0 (and compatible models).

Endpoint: POST https://ark.ap-southeast.bytepluses.com/api/v3/images/generations

Usage:
    # Text-to-image
    python scripts/generate_image_byteplus.py \
        --prompt "documentary phone-mirror selfie, young woman post-workout, amateur iPhone quality" \
        --output gym.jpeg

    # Single reference image (image-to-image)
    python scripts/generate_image_byteplus.py \
        --prompt "Put the bottle from image 1 on the sink of this gym scene" \
        --ref ~/Desktop/norra-ad-30s/refs/anchor_01_v3_byredo.png \
        --output gym_with_bottle.jpeg

    # Multiple reference images
    python scripts/generate_image_byteplus.py \
        --prompt "Replace the clothing in image 1 with the outfit from image 2" \
        --ref character.png --ref outfit.png \
        --output result.jpeg

    # Sequential / series (multiple images from one call)
    python scripts/generate_image_byteplus.py \
        --prompt "Four seasons of the same courtyard — winter, spring, summer, autumn" \
        --sequential 4 \
        --output seasons.jpeg  # outputs seasons_0.jpeg, seasons_1.jpeg, ...

    # Portrait 9:16 (Seedance-friendly)
    python scripts/generate_image_byteplus.py --prompt "..." --size 1440x2560 --output clip.jpeg

Size options:
    Preset:   "1K", "2K"    (model picks aspect based on prompt/reference)
    Explicit: "WxH"         (min total pixels: 3,686,400 = 1920x1920 area)
    Portrait 9:16 minimums: 1440x2560
    Landscape 16:9 minimums: 2560x1440

Pricing: per-image token-based, see BytePlus console.

WHY THIS EXISTS (vs generate_image.py which uses Nano Banana 2):
    Seedream 5.0 outputs are "BytePlus-native" → Seedance 2.0 accepts them as
    input references despite containing photorealistic faces. This is the only
    practical way to use AI-generated characters in Seedance video generation,
    since Seedance blocks all non-BytePlus photoreal faces with
    InputImageSensitiveContentDetected.PrivacyInformation.

    CRITICAL GOTCHA: Seedream outputs with `--ref` image references tend to be
    *too photoreal* and can STILL trip Seedance's filter. Text-only Seedream
    outputs (no --ref) have a slightly softer AI aesthetic that reliably passes.
    See reference/learnings.md → "Seedream→Seedance filter threshold".

    To get past the filter with reference images, use documentary / amateur
    prompt language (see reference/seedream.md → "Documentary prompt pattern").

Requires:
    ARK_API_KEY in environment (BytePlus Ark)
    S3_BUCKET (+S3_REGION) if passing local image files to --ref (auto-uploaded to S3; see media_host.py)
"""
import os, sys, argparse, json, urllib.request, urllib.error


ARK_BASE = "https://ark.ap-southeast.bytepluses.com/api/v3"
DEFAULT_MODEL = "seedream-5-0-260128"


def upload_to_host(local_path, prefix="seedream"):
    """Upload a local file to the configured host (S3 default, R2 legacy); returns a fetchable URL."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from media_host import upload_public
    return upload_public(local_path, prefix)


def resolve_ref(ref):
    """Accept either a URL or a local file. Local files auto-upload to S3."""
    if ref.startswith(("http://", "https://")):
        return ref
    if not os.path.exists(ref):
        print(f"ERROR: Reference file not found: {ref}")
        sys.exit(1)
    print(f"Uploading {ref} to S3...")
    url = upload_to_host(ref)
    if not url:
        print(f"ERROR: upload failed. Use a URL directly, or set S3_BUCKET (+S3_REGION).")
        sys.exit(1)
    print(f"  -> {url}")
    return url


def download(url, path):
    """Download an image URL to a local path."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    urllib.request.urlretrieve(url, path)
    return os.path.getsize(path)


def main():
    p = argparse.ArgumentParser(
        description="Generate images with BytePlus Seedream 5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--prompt", required=True, help="Generation prompt")
    p.add_argument("--output", required=True,
                   help="Output file path (.jpeg/.png). For sequential, _0/_1/... suffixes added.")
    p.add_argument("--ref", action="append", default=[],
                   help="Reference image (local path or URL; repeatable for multi-image)")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    p.add_argument("--size", default="2K",
                   help="Image size: '1K', '2K', or 'WxH' (min 3,686,400 px area)")
    p.add_argument("--sequential", type=int, default=None,
                   help="Generate a series of N images (1-6). Implies sequential_image_generation=auto.")
    p.add_argument("--watermark", action="store_true", default=False,
                   help="Include the BytePlus watermark (default: off)")
    p.add_argument("--seed", type=int, default=None, help="Random seed (if supported)")
    p.add_argument("--skip-existing", action="store_true", help="Skip if output already exists")
    args = p.parse_args()

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return

    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("ERROR: ARK_API_KEY not set. Run: source ~/Downloads/ai-film-skills/config.env")
        sys.exit(1)

    # Resolve reference images
    refs = [resolve_ref(r) for r in args.ref]

    # Build body
    body = {
        "model": args.model,
        "prompt": args.prompt,
        "response_format": "url",
        "size": args.size,
        "stream": False,
        "watermark": args.watermark,
    }
    if len(refs) == 1:
        body["image"] = refs[0]
    elif len(refs) > 1:
        body["image"] = refs
    if args.sequential:
        body["sequential_image_generation"] = "auto"
        body["sequential_image_generation_options"] = {"max_images": args.sequential}
    else:
        body["sequential_image_generation"] = "disabled"
    if args.seed is not None:
        body["seed"] = args.seed

    # Submit
    print(f"Seedream {args.model} | size={args.size} | refs={len(refs)} | sequential={args.sequential or 1}")
    print(f"  Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")

    req = urllib.request.Request(
        f"{ARK_BASE}/images/generations",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
    )
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR (HTTP {e.code}): {err_body}")
        sys.exit(1)

    # Extract image URLs and download
    data = result.get("data") or []
    if not data:
        print(f"ERROR: no images in response:\n{json.dumps(result, indent=2)}")
        sys.exit(1)

    base, ext = os.path.splitext(args.output)
    if not ext:
        ext = ".jpeg"

    paths = []
    if len(data) == 1:
        url = data[0].get("url")
        if not url:
            print(f"ERROR: no url in response: {data[0]}")
            sys.exit(1)
        size_bytes = download(url, args.output)
        paths.append(args.output)
        print(f"SAVED {args.output} ({size_bytes/1024:.1f} KB, {data[0].get('size','?')})")
    else:
        for i, d in enumerate(data):
            url = d.get("url")
            if not url:
                continue
            path = f"{base}_{i}{ext}"
            size_bytes = download(url, path)
            paths.append(path)
            print(f"SAVED {path} ({size_bytes/1024:.1f} KB, {d.get('size','?')})")

    # Usage report
    usage = result.get("usage", {})
    if usage:
        print(f"Usage: {usage}")


if __name__ == "__main__":
    main()

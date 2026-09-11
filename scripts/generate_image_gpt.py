#!/usr/bin/env python3
"""Generate / edit images with OpenAI GPT Image (gpt-image-2, gpt-image-2.5-flare, gpt-image-2.5-sunburst).
Default still-image model family since Sept 2026.

Same CLI shape as the old Gemini script so pipelines swap 1:1:
    --prompt --output [--ref img ...] [--edit img] [--aspect] [--size] [--quality] [--skip-existing]

Models (--model, or GPT_IMAGE_MODEL in ~/config.env to change the default):
    sunburst     = gpt-image-2.5-sunburst       DEFAULT since 2026-09-11 — 2.5 base model: best quality, most precise edits
    flare        = gpt-image-2.5-flare          2.5 small model: fastest — previs, storyboard coverage, variants
    gpt-image-2  (alias "2")                   previous default; rollback and the automatic fallback
  2.5 adds --quality xhigh | max. If the key's project has no access to a 2.5 model (rollout / project model
  allowlist / org verification), the script falls back to gpt-image-2 (xhigh/max -> high) and says so;
  --no-fallback turns that into an error. Other models never fall back.
  Before changing a workflow's default model, A/B it: scripts/compare_image_models.py.

Usage:
    source ~/config.env   # OPENAI_API_KEY

    # Text-to-image (16:9 default -> 1536x864)
    python scripts/generate_image_gpt.py --prompt "A narrow Kyoto street at dusk, lanterns, light rain" --output scene_01.png

    # With reference images (character sheet + set) -> uses the edits endpoint with all refs attached
    python scripts/generate_image_gpt.py --prompt "Use the attached references. Same face, same room layout. [SCENE]" \
        --ref refs/character.png --ref refs/set_wide.png --output scene_02.png

    # Fast previs on the 2.5 small model (the default is Sunburst)
    python scripts/generate_image_gpt.py --model flare --quality medium --prompt "..." --ref refs/character.png --output previs.png

    # Edit / inpaint an existing image (optionally with a mask: transparent = area to change)
    python scripts/generate_image_gpt.py --prompt "Remove the person" --edit source.png --output clean.png
    python scripts/generate_image_gpt.py --prompt "Replace the label text with NORRA" --edit bottle.png --mask label_mask.png --output bottle_v2.png

    # Resolution / quality / transparency
    python scripts/generate_image_gpt.py --prompt "..." --aspect 9:16 --size 4K --quality high --output hero.png
    python scripts/generate_image_gpt.py --prompt "flat logo, white on transparent" --aspect 1:1 --transparent --output logo.png

Sizes (max edge 3840, multiples of 16, ratio <= 3:1, 655,360-8,294,400 px; above 2560x1440 is experimental):
    --aspect 16:9 -> 1536x864 (1K)  | 2048x1152 (2K) | 3840x2160 (4K)
    --aspect 9:16 -> 864x1536 (1K)  | 1152x2048 (2K) | 2160x3840 (4K)
    --aspect 3:2  -> 1536x1024 (1K) — the pre-2.3 "16:9" default; 2:3 -> 1024x1536
    --aspect 1:1  -> 1024x1024 (1K) | 2048x2048 (2K)
    --aspect 21:9 -> 1536x656 (1K)  | 2048x880 (2K)  | 3840x1648 (4K)
    or pass --size WxH directly.

Cost: token-billed, same rates for 2 and 2.5 ($5/M text in, $8/M image in, $30/M image out). A 1K medium still is
~1.4k output tokens (~$0.04). The script prints tokens and the estimated $ for every call. Text/typography rendering
is a strength — use it for packaging, titles and end cards where Nano Banana garbled letters.
"""
import argparse
import base64
import os
import sys
import time

SIZES = {
    "16:9": {"1K": "1536x864", "2K": "2048x1152", "4K": "3840x2160"},
    "9:16": {"1K": "864x1536", "2K": "1152x2048", "4K": "2160x3840"},
    "3:2": {"1K": "1536x1024", "2K": "2400x1600", "4K": "3504x2336"},
    "2:3": {"1K": "1024x1536", "2K": "1600x2400", "4K": "2336x3504"},
    "1:1": {"1K": "1024x1024", "2K": "2048x2048", "4K": "2880x2880"},
    "21:9": {"1K": "1536x656", "2K": "2048x880", "4K": "3840x1648"},
    "4:3": {"1K": "1408x1056", "2K": "2048x1536", "4K": "3264x2448"},
    "3:4": {"1K": "1056x1408", "2K": "1536x2048", "4K": "2448x3264"},
}
MODELS = {
    "2": "gpt-image-2",
    "flare": "gpt-image-2.5-flare",
    "sunburst": "gpt-image-2.5-sunburst",
}
FALLBACK_MODEL = "gpt-image-2"
FALLBACK_ELIGIBLE_PREFIX = "gpt-image-2.5"  # only 2.5 models fall back; typos and other ids fail loudly
DEFAULT_MODEL = os.environ.get("GPT_IMAGE_MODEL", "gpt-image-2.5-sunburst")
QUALITIES = ["low", "medium", "high", "xhigh", "max", "auto"]
QUALITIES_25_ONLY = {"xhigh", "max"}
# USD per 1M tokens — text in, image in, image out. Only models listed here get a $ estimate.
RATES = {"gpt-image-2": (5.0, 8.0, 30.0), "gpt-image-2.5": (5.0, 8.0, 30.0)}


def resolve_model(name):
    return MODELS.get(name, name)


def supports_25_quality(model):
    return model.startswith("gpt-image-2.5")


def is_access_error(e):
    """True only for the API's 'this project cannot use this model' errors (403/404 + model_not_found / verification)."""
    code = getattr(e, "code", None)
    status = getattr(e, "status_code", None)
    msg = str(e)
    return (code == "model_not_found" or
            (status in (403, 404) and ("does not have access to model" in msg or "must be verified to use the model" in msg)))


def estimate_usd(model, usage):
    """Estimated $ for one response, or None when the model's price or the usage counters are unknown."""
    try:
        rates = next((r for prefix, r in sorted(RATES.items(), key=lambda kv: -len(kv[0])) if model.startswith(prefix)), None)
        if not rates or usage is None or usage.output_tokens is None or usage.input_tokens is None:
            return None
        details = getattr(usage, "input_tokens_details", None)
        text_in = getattr(details, "text_tokens", None) if details else None
        image_in = getattr(details, "image_tokens", None) if details else None
        if text_in is None:
            text_in, image_in = usage.input_tokens, 0
        return (text_in * rates[0] + (image_in or 0) * rates[1] + usage.output_tokens * rates[2]) / 1e6
    except (TypeError, AttributeError):
        return None


def output_format_for(output, transparent, log=print):
    """(output path, api output_format). Transparency forces png when a .jpg name was given."""
    base, ext = os.path.splitext(output)
    ext = ext.lower().lstrip(".") or "png"
    fmt = {"jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}.get(ext, "png")
    if transparent and fmt == "jpeg":
        output = base + ".png"
        log(f"NOTE: transparency needs png/webp; writing {output}")
        fmt = "png"
    return output, fmt


def generate(prompt, output, images=(), mask=None, size="1536x864", quality="high", model=DEFAULT_MODEL,
             transparent=False, moderation="auto", n=1, retries=3, fallback=True, log=print):
    """Generate (no images) or edit (images[0] first) and save to `output` (+ output_2 ... for n > 1).

    Returns dict(model, size, quality, seconds, input_tokens, output_tokens, usd, files).
    Raises RuntimeError on failure. On an access error for a 2.5 model it retries on gpt-image-2 unless fallback=False.
    """
    if retries < 1:
        raise RuntimeError("retries must be >= 1")
    try:
        from openai import OpenAI
        client = OpenAI()
        output, fmt = output_format_for(output, transparent, log)
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    except Exception as e:  # setup errors are reported like API errors, never as a crash
        raise RuntimeError(f"setup failed: {e}")
    ext = os.path.splitext(output)[1].lstrip(".") or "png"
    images = list(images)
    mode = "edit" if images else "generate"
    model = resolve_model(model)

    attempt = 0
    while True:
        q = quality
        if q in QUALITIES_25_ONLY and not supports_25_quality(model):
            log(f"NOTE: quality={q} exists only on GPT Image 2.5; using high on {model}")
            q = "high"
        common = dict(model=model, prompt=prompt, size=size, quality=q, n=n, output_format=fmt, moderation=moderation)
        if transparent:
            common["background"] = "transparent"
        log(f"GPT Image | {model} | {mode} | {size} | quality={q} | refs={len(images)}")
        image_handles, mask_handle = [], None
        try:
            t0 = time.time()
            if mode == "edit":
                image_handles = [open(pth, "rb") for pth in images]
                kwargs = dict(common, image=list(image_handles) if len(image_handles) > 1 else image_handles[0])
                kwargs.pop("moderation", None)  # images.edit() does not accept moderation
                if mask:
                    mask_handle = open(mask, "rb")
                    kwargs["mask"] = mask_handle
                result = client.images.edit(**kwargs)
            else:
                result = client.images.generate(**common)
            seconds = time.time() - t0
        except Exception as e:
            if is_access_error(e):
                if fallback and model.startswith(FALLBACK_ELIGIBLE_PREFIX):
                    log(f"NOTE: this key has no access to {model} yet ({e}). Falling back to {FALLBACK_MODEL}. "
                        "Check the project's allowed models / API Organization Verification on platform.openai.com.")
                    model = FALLBACK_MODEL
                    continue
                raise RuntimeError(f"no access to {model}: {e}")
            if isinstance(e, OSError):  # unreadable ref/mask: retrying cannot help
                raise RuntimeError(f"cannot read input: {e}")
            attempt += 1
            log(f"ERROR (attempt {attempt}/{retries}): {e}")
            if attempt >= retries:
                raise RuntimeError(f"failed after {retries} attempts: {e}")
            time.sleep(3 * attempt)
            continue
        finally:
            for h in image_handles + ([mask_handle] if mask_handle else []):
                try:
                    h.close()
                except Exception:
                    pass

        # Success: save and account outside the retry loop — a bookkeeping error must never trigger a re-generation.
        files = []
        for i, item in enumerate(result.data):
            out = output if i == 0 else f"{os.path.splitext(output)[0]}_{i + 1}.{ext}"
            with open(out, "wb") as f:
                f.write(base64.b64decode(item.b64_json))
            files.append(out)
        usage = getattr(result, "usage", None)
        return dict(model=model, size=size, quality=q, seconds=round(seconds, 1),
                    input_tokens=getattr(usage, "input_tokens", None),
                    output_tokens=getattr(usage, "output_tokens", None),
                    usd=estimate_usd(model, usage), files=files)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prompt", required=True)
    p.add_argument("--output", required=True, help="Output file (.png/.jpg/.webp)")
    p.add_argument("--ref", action="append", default=[], help="Reference image (repeatable). Uses the edits endpoint")
    p.add_argument("--edit", default=None, help="Source image to edit (first image in the edit request)")
    p.add_argument("--mask", default=None, help="PNG mask for --edit (transparent = editable area)")
    p.add_argument("--aspect", default="16:9", choices=list(SIZES.keys()))
    p.add_argument("--size", default="1K", help="1K | 2K | 4K | WxH (e.g. 1536x864)")
    p.add_argument("--quality", default="high", choices=QUALITIES, help="xhigh/max: GPT Image 2.5 only")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"sunburst | flare | gpt-image-2 (alias 2) | any full model id (default: {DEFAULT_MODEL})")
    p.add_argument("--no-fallback", action="store_true", help="Fail instead of falling back to gpt-image-2")
    p.add_argument("--transparent", action="store_true", help="Transparent background (png/webp)")
    p.add_argument("--moderation", default="auto", choices=["auto", "low"])
    p.add_argument("--n", type=int, default=1, help="Variants (saved as output, output_2, ...)")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--skip-existing", action="store_true")
    args = p.parse_args()
    if args.retries < 1:
        p.error("--retries must be >= 1")
    if args.mask and not (args.edit or args.ref):
        p.error("--mask needs --edit")

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set. Run: source ~/config.env", file=sys.stderr)
        sys.exit(1)

    size = SIZES[args.aspect].get(args.size.upper(), args.size)
    images = ([args.edit] if args.edit else []) + list(args.ref)
    try:
        r = generate(args.prompt, args.output, images=images, mask=args.mask, size=size, quality=args.quality,
                     model=args.model, transparent=args.transparent, moderation=args.moderation, n=args.n,
                     retries=args.retries, fallback=not args.no_fallback)
    except RuntimeError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
    tok = f" | tokens in/out {r['input_tokens']}/{r['output_tokens']}" if r["output_tokens"] is not None else ""
    usd = f" | ~${r['usd']:.3f}" if r["usd"] is not None else ""
    print(f"SAVED {', '.join(r['files'])} ({r['size']}, {r['model']}, {r['quality']}) in {int(r['seconds'])}s{tok}{usd}")


if __name__ == "__main__":
    main()

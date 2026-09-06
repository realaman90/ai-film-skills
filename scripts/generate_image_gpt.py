#!/usr/bin/env python3
"""Generate / edit images with OpenAI GPT Image 2 (gpt-image-2). Default still-image model since Sept 2026.

Same CLI shape as the old Gemini script so pipelines swap 1:1:
    --prompt --output [--ref img ...] [--edit img] [--aspect] [--size] [--quality] [--skip-existing]

Usage:
    source ~/config.env   # OPENAI_API_KEY

    # Text-to-image (16:9 default -> 1536x1024)
    python scripts/generate_image_gpt.py --prompt "A narrow Kyoto street at dusk, lanterns, light rain" --output scene_01.png

    # With reference images (character sheet + set) -> uses the edits endpoint with all refs attached
    python scripts/generate_image_gpt.py --prompt "Use the attached references. Same face, same room layout. [SCENE]" \
        --ref refs/character.png --ref refs/set_wide.png --output scene_02.png

    # Edit / inpaint an existing image (optionally with a mask: transparent = area to change)
    python scripts/generate_image_gpt.py --prompt "Remove the person" --edit source.png --output clean.png
    python scripts/generate_image_gpt.py --prompt "Replace the label text with NORRA" --edit bottle.png --mask label_mask.png --output bottle_v2.png

    # Resolution / quality / transparency
    python scripts/generate_image_gpt.py --prompt "..." --aspect 9:16 --size 4K --quality high --output hero.png
    python scripts/generate_image_gpt.py --prompt "flat logo, white on transparent" --aspect 1:1 --transparent --output logo.png

Sizes (max edge 3840, multiples of 16, ratio <= 3:1):
    --aspect 16:9 -> 1536x1024 (1K) | 2048x1152 (2K) | 3840x2160 (4K)
    --aspect 9:16 -> 1024x1536 (1K) | 1152x2048 (2K) | 2160x3840 (4K)
    --aspect 1:1  -> 1024x1024 (1K) | 2048x2048 (2K)
    --aspect 21:9 -> 2048x880 (2K)  | 3840x1648 (4K)
    or pass --size WxH directly.

Cost (Sept 2026): ~$0.03 (1K) · $0.05 (2K) · $0.08 (4K) per image. Text/typography rendering is a strength —
use it for packaging, titles, and end cards where Nano Banana garbled letters.
"""
import argparse
import base64
import os
import sys
import time

SIZES = {
    "16:9": {"1K": "1536x1024", "2K": "2048x1152", "4K": "3840x2160"},
    "9:16": {"1K": "1024x1536", "2K": "1152x2048", "4K": "2160x3840"},
    "1:1": {"1K": "1024x1024", "2K": "2048x2048", "4K": "2048x2048"},
    "21:9": {"1K": "1536x656", "2K": "2048x880", "4K": "3840x1648"},
    "4:3": {"1K": "1408x1056", "2K": "2048x1536", "4K": "3840x2880"},
    "3:4": {"1K": "1056x1408", "2K": "1536x2048", "4K": "2880x3840"},
}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prompt", required=True)
    p.add_argument("--output", required=True, help="Output file (.png/.jpg/.webp)")
    p.add_argument("--ref", action="append", default=[], help="Reference image (repeatable). Uses the edits endpoint")
    p.add_argument("--edit", default=None, help="Source image to edit (first image in the edit request)")
    p.add_argument("--mask", default=None, help="PNG mask for --edit (transparent = editable area)")
    p.add_argument("--aspect", default="16:9", choices=list(SIZES.keys()))
    p.add_argument("--size", default="1K", help="1K | 2K | 4K | WxH (e.g. 1536x1024)")
    p.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    p.add_argument("--model", default="gpt-image-2", help="gpt-image-2 (default) | gpt-image-2-2026-04-21 | gpt-image-1.5 ...")
    p.add_argument("--transparent", action="store_true", help="Transparent background (png/webp)")
    p.add_argument("--moderation", default="auto", choices=["auto", "low"])
    p.add_argument("--n", type=int, default=1, help="Variants (saved as output, output_2, ...)")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--skip-existing", action="store_true")
    args = p.parse_args()

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set. Run: source ~/config.env", file=sys.stderr)
        sys.exit(1)
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: pip install openai", file=sys.stderr)
        sys.exit(1)

    size = SIZES[args.aspect].get(args.size.upper(), args.size)
    ext = os.path.splitext(args.output)[1].lower().lstrip(".") or "png"
    fmt = {"jpg": "jpeg", "jpeg": "jpeg", "webp": "webp"}.get(ext, "png")
    if args.transparent and fmt == "jpeg":
        print("NOTE: transparency needs png/webp; switching output_format to png")
        fmt = "png"

    client = OpenAI()
    common = dict(model=args.model, prompt=args.prompt, size=size, quality=args.quality, n=args.n,
                  output_format=fmt, moderation=args.moderation)
    if args.transparent:
        common["background"] = "transparent"

    images = ([args.edit] if args.edit else []) + list(args.ref)
    mode = "edit" if images else "generate"
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    print(f"GPT Image 2 | {mode} | {size} | quality={args.quality} | refs={len(images)}")

    for attempt in range(args.retries):
        handles = []
        try:
            t0 = time.time()
            if mode == "edit":
                handles = [open(pth, "rb") for pth in images]
                kwargs = dict(common, image=handles if len(handles) > 1 else handles[0])
                kwargs.pop("moderation", None)  # images.edit() does not accept moderation
                if args.mask:
                    handles.append(open(args.mask, "rb"))
                    kwargs["mask"] = handles[-1]
                result = client.images.edit(**kwargs)
            else:
                result = client.images.generate(**common)
            saved = []
            for i, item in enumerate(result.data):
                out = args.output if i == 0 else f"{os.path.splitext(args.output)[0]}_{i + 1}.{ext}"
                with open(out, "wb") as f:
                    f.write(base64.b64decode(item.b64_json))
                saved.append(out)
            usage = getattr(result, "usage", None)
            tok = f" | tokens in/out {usage.input_tokens}/{usage.output_tokens}" if usage else ""
            print(f"SAVED {', '.join(saved)} ({size}) in {int(time.time() - t0)}s{tok}")
            return
        except Exception as e:
            print(f"ERROR (attempt {attempt + 1}/{args.retries}): {e}")
            if attempt < args.retries - 1:
                time.sleep(3 * (attempt + 1))
        finally:
            for h in handles:
                try:
                    h.close()
                except Exception:
                    pass
    print(f"FAILED after {args.retries} attempts")
    sys.exit(1)


if __name__ == "__main__":
    main()

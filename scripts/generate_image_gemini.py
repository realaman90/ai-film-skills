"""(FALLBACK — the default still model is GPT Image 2.5 Sunburst: scripts/generate_image_gpt.py)
Generate a single image using Nano Banana 2.1 (Gemini image generation; GA 2026-10-06).

Usage:
    # Text-to-image
    python scripts/generate_image_gemini.py --prompt "A cat on a hill at sunset" --output cat.png

    # With character reference image
    python scripts/generate_image_gemini.py --prompt "Same person walking in rain" --ref refs/char.png --output scene.png

    # With aspect ratio and resolution
    python scripts/generate_image_gemini.py --prompt "..." --output scene.png --aspect 16:9 --size 2K

    # Edit existing image
    python scripts/generate_image_gemini.py --prompt "Remove the person" --edit source.png --output edited.png

    # Multiple reference images
    python scripts/generate_image_gemini.py --prompt "..." --ref ref1.png --ref ref2.png --output scene.png

    # Older Nano Banana 2 / Pro / Lite
    python scripts/generate_image_gemini.py --model nb2|pro|lite --prompt "..." --output scene.png
"""
import os, sys, io, argparse, time

def main():
    parser = argparse.ArgumentParser(description="Generate image with Nano Banana 2.1")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--output", required=True, help="Output file path (.png)")
    parser.add_argument("--ref", action="append", default=[], help="Reference image path (repeatable, up to 14 on 2.1)")
    parser.add_argument("--edit", default=None, help="Source image to edit (inpainting/modification)")
    parser.add_argument("--aspect", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--size", default=None, help="Image size: 512, 1K, 2K, 4K")
    parser.add_argument("--model", default="nb21",
                        help="nb21 = gemini-nano-banana-2.1 (Nano Banana 2.1, default since 2026-10-06: better editing, typography, "
                             "subject consistency; ~$0.034 at 1K) | nb2 = gemini-3.1-flash-image (Nano Banana 2) | pro = gemini-3-pro-image "
                             "(Nano Banana Pro: best typography/likeness, slower) | lite = gemini-3.1-flash-lite-image (cheap drafts) | "
                             "or any raw model id")
    parser.add_argument("--retries", type=int, default=3, help="Max retry attempts")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if output already exists")
    args = parser.parse_args()

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return

    from google import genai
    from google.genai import types
    from PIL import Image

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    MODEL_ALIASES = {
        "nb21": "gemini-nano-banana-2.1",
        "2.1": "gemini-nano-banana-2.1",
        "nb2": "gemini-3.1-flash-image",
        "pro": "gemini-3-pro-image",
        "lite": "gemini-3.1-flash-lite-image",
    }
    args.model = MODEL_ALIASES.get(args.model, args.model)

    # Build config
    image_config_kwargs = {"aspect_ratio": args.aspect}
    if args.size:
        if "image_size" in getattr(types.ImageConfig, "model_fields", {}):
            image_config_kwargs["image_size"] = args.size
        else:
            print(f"NOTE: installed google-genai has no ImageConfig.image_size; ignoring --size {args.size} "
                  "(default output ~1376x768 for 16:9 is fine for video first frames)")

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(**image_config_kwargs),
    )

    # Build content
    contents = []

    if args.edit:
        # Edit mode: load source image
        source = Image.open(args.edit)
        buf = io.BytesIO()
        source.save(buf, format="PNG")
        contents.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png"))
    elif args.ref:
        # Reference mode: load reference images
        for ref_path in args.ref:
            ref_img = Image.open(ref_path)
            contents.append(ref_img)

    contents.append(args.prompt)

    # Generate with retry
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    for attempt in range(args.retries):
        try:
            print(f"Generating with {args.model} (attempt {attempt+1}/{args.retries})...")
            response = client.models.generate_content(
                model=args.model,
                contents=contents,
                config=config,
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    img = Image.open(io.BytesIO(part.inline_data.data))
                    img.save(args.output)
                    print(f"SAVED {args.output} ({img.size[0]}x{img.size[1]})")
                    return
            print("No image in response")
        except Exception as e:
            print(f"ERROR: {e}")
            if attempt < args.retries - 1:
                time.sleep(3 * (attempt + 1))

    print(f"FAILED after {args.retries} attempts")
    sys.exit(1)

if __name__ == "__main__":
    main()

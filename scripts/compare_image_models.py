#!/usr/bin/env python3
"""A/B the GPT Image models on the SAME prompt, refs, size and quality — OpenAI's own migration procedure.

Run this before changing a workflow's default still model (e.g. gpt-image-2 -> gpt-image-2.5-flare). Keep the prompt,
references, dimensions and quality identical for the first comparison; repeat (--runs 2) to see consistency.

Usage:
    source ~/config.env
    python scripts/compare_image_models.py --prompt "$(cat prompts/scene_03.txt)" \
        --ref refs/character.png --ref refs/set_wide.png --aspect 16:9 --quality medium --runs 2 --out refs/ab/scene_03

    # identity edit chain / label fix
    python scripts/compare_image_models.py --prompt "Change only the label text to 'NORRA'. Keep ..." \
        --edit storyboard/product.png --quality high --out refs/ab/label

Writes <out>/<model>_r<N>.png, results.json (seconds, tokens, $ per image, errors) and compare.html (side by side,
open it in the browser). A model the key cannot access is recorded as an error — no fallback here, on purpose.
xhigh/max exist only on GPT Image 2.5, so they are refused when gpt-image-2 is in the set (no mixed-quality A/B).
Exit status: 0 if at least one image was produced, 1 otherwise.

Judge each column on: instruction following, identity/product preservation, exact text, unwanted changes, alpha
(transparent assets), then latency and $ per ACCEPTED image. Switch only when quality holds.
"""
import argparse
import html
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_image_gpt import QUALITIES, QUALITIES_25_ONLY, SIZES, generate, resolve_model, supports_25_quality  # noqa: E402

DEFAULT_MODELS = "gpt-image-2,flare,sunburst"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--models", default=DEFAULT_MODELS, help=f"Comma list (default {DEFAULT_MODELS})")
    p.add_argument("--ref", action="append", default=[])
    p.add_argument("--edit", default=None)
    p.add_argument("--mask", default=None)
    p.add_argument("--aspect", default="16:9", choices=list(SIZES.keys()))
    p.add_argument("--size", default="1K")
    p.add_argument("--quality", default="medium", choices=QUALITIES)
    p.add_argument("--transparent", action="store_true")
    p.add_argument("--runs", type=int, default=1, help="Repeats per model (consistency check)")
    p.add_argument("--workers", type=int, default=3, help="Parallel requests (tier-1 limit is 5 images/min)")
    args = p.parse_args()

    models = list(dict.fromkeys(resolve_model(m.strip()) for m in args.models.split(",") if m.strip()))
    if not models:
        p.error("--models is empty")
    if args.runs < 1:
        p.error("--runs must be >= 1")
    if args.quality in QUALITIES_25_ONLY and not all(supports_25_quality(m) for m in models):
        p.error(f"quality={args.quality} exists only on GPT Image 2.5; compare at high, or drop the non-2.5 models")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("ERROR: OPENAI_API_KEY not set. Run: source ~/config.env")
    os.makedirs(args.out, exist_ok=True)
    size = SIZES[args.aspect].get(args.size.upper(), args.size)
    images = ([args.edit] if args.edit else []) + list(args.ref)
    jobs = [(m, r) for m in models for r in range(1, args.runs + 1)]

    def run(job):
        model, r = job
        out = os.path.join(args.out, f"{model}_r{r}.png")
        try:
            res = generate(args.prompt, out, images=images, mask=args.mask, size=size, quality=args.quality,
                           model=model, transparent=args.transparent, retries=2, fallback=False,
                           log=lambda s, m=model: print(f"[{m} r{r}] {s}"))
            res.update(run=r, file=os.path.basename(res["files"][0]), error=None)
        except Exception as e:  # one bad job must not lose the other (paid) results
            res = dict(model=model, run=r, file=None, error=f"{type(e).__name__}: {e}"[:400])
        print(f"[{model} r{r}] {'ERROR ' + res['error'][:120] if res['error'] else 'done in %ss' % res['seconds']}")
        return res

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        results = list(ex.map(run, jobs))

    meta = dict(prompt=args.prompt, refs=images, mask=args.mask, size=size, quality=args.quality, results=results)
    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(meta, f, indent=2)

    cards = []
    for res in results:
        if res["error"]:
            body = f'<div class="err">{html.escape(res["error"])}</div>'
        else:
            usd = f' · ~${res["usd"]:.3f}' if res.get("usd") is not None else ""
            body = (f'<a href="{res["file"]}"><img src="{res["file"]}"></a>'
                    f'<div class="m">{res["seconds"]} s · {res.get("output_tokens")} out tok{usd} · q={res["quality"]}</div>')
        cards.append(f'<figure><figcaption>{html.escape(res["model"])} · run {res["run"]}</figcaption>{body}</figure>')
    refs = "".join(f'<li>{html.escape(x)}</li>' for x in images) or "<li>none (text-to-image)</li>"
    page = f"""<!doctype html><meta charset="utf-8"><title>GPT Image A/B</title>
<style>body{{font:14px system-ui;margin:24px;background:#f6f6f4;color:#111}}pre{{white-space:pre-wrap;background:#fff;padding:12px;border:1px solid #ddd}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px}}figure{{margin:0;background:#fff;border:1px solid #ddd;padding:8px}}
img{{width:100%;display:block}}figcaption{{font-weight:600;margin-bottom:6px}}.m{{color:#555;margin-top:6px}}.err{{color:#a00;min-height:120px}}</style>
<h1>GPT Image A/B — {html.escape(size)} · quality {html.escape(args.quality)}</h1>
<p>Judge: instruction following · identity / product preservation · exact text · unwanted changes · alpha · then latency and $ per accepted image.</p>
<details><summary>Prompt + refs</summary><pre>{html.escape(args.prompt)}</pre><ul>{refs}</ul></details>
<div class="g">{''.join(cards)}</div>"""
    with open(os.path.join(args.out, "compare.html"), "w") as f:
        f.write(page)
    ok = sum(1 for r in results if not r["error"])
    print(f"WROTE {args.out}/compare.html + results.json ({ok}/{len(results)} images)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

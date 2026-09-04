# GPT Image 2 — Stills (default image model since 2026-09)

OpenAI `gpt-image-2` (snapshot `gpt-image-2-2026-04-21`, released 2026-04-21). Replaces Nano Banana 2 for character
sheets, set references, storyboard stills, product shots and anything with **text/typography** (packaging, titles).
Nano Banana stays available as a fallback (`scripts/generate_image_gemini.py`); Seedream 5 (`generate_image_byteplus.py`)
stays for the Seedance face-filter workaround. Docs: https://developers.openai.com/api/docs/guides/image-generation

Script: `scripts/generate_image_gpt.py` (openai SDK ≥ 2.0, `OPENAI_API_KEY`). Same flags as the old script:
`--prompt --output --ref --edit --aspect --size --skip-existing`, plus `--quality --mask --transparent --n`.

## Endpoints the script uses

| Mode | When | API |
|---|---|---|
| generate | no `--ref` / `--edit` | `client.images.generate(model, prompt, size, quality, output_format, background, moderation, n)` |
| edit | any `--ref` or `--edit` (+ optional `--mask`) | `client.images.edit(model, image=[...], mask, prompt, ...)` — all refs are sent as `image[]`; `--edit` goes first |

Output is `b64_json` → written as png/jpeg/webp (from the output extension). Transparent backgrounds need png/webp.

## Sizes

Max edge 3840 px, multiples of 16, ratio ≤ 3:1, 655k–8.3M pixels.

| `--aspect` | `--size 1K` | `2K` | `4K` |
|---|---|---|---|
| 16:9 | 1536×1024 | 2048×1152 | 3840×2160 |
| 9:16 | 1024×1536 | 1152×2048 | 2160×3840 |
| 1:1 | 1024×1024 | 2048×2048 | — |
| 21:9 | 1536×656 | 2048×880 | 3840×1648 |

Or `--size WxH`. For video first frames 1K is plenty (Omni/LTX/Seedance resample anyway); use 2K/4K for print,
packaging close-ups and end cards you will crop.

Cost (Sept 2026): ≈ $0.03 (1K) · $0.05 (2K) · $0.08 (4K) per image; token-billed ($8/M image input, $30/M output).
Rate limit tier 1 = 5 images/min — parallelize at most 4 stills at a time.

## Prompting GPT Image 2

- Brief it like an art director: subject → action → environment → composition/lens → light → grade/medium. Full sentences.
- **Text renders reliably**: put label copy in quotes (*the label reads "NORRA"*). Still verify letters on packaging.
- **Reference images work through the edit endpoint**: say what each is for — *"Image 1 is the character (keep the face
  identical), image 2 is the room (keep the layout)"*. Up to ~4 refs keeps fidelity high.
- `--edit` + `--mask` for true inpainting (transparent mask pixels = editable). Without a mask it re-imagines the
  whole frame while preserving the subject.
- `--quality medium` for storyboard coverage, `high` for hero stills / anything that becomes a first frame.
- `--transparent` for logos and overlays destined for HyperFrames.
- Moderation: `--moderation low` only relaxes borderline filtering; real-person likeness of public figures is refused.

## Verified 2026-09-04

`--aspect 16:9 --size 1K --quality medium`: 1536×1024 product still with the label text "NORRA" rendered correctly,
38 s, 54 input / 1372 output tokens. Used directly as the Omni first frame — composition preserved.

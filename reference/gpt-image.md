# GPT Image — Stills (default image model family since 2026-09)

OpenAI GPT Image replaces Nano Banana 2 for character sheets, set references, storyboard stills, product shots and
anything with **text/typography** (packaging, titles). Nano Banana stays available as a fallback
(`scripts/generate_image_gemini.py`); Seedream 5 (`generate_image_byteplus.py`) stays for the Seedance face-filter
workaround. Docs: https://developers.openai.com/api/docs/guides/image-generation ·
prompting: https://developers.openai.com/api/docs/guides/image-prompting

Script: `scripts/generate_image_gpt.py` (openai SDK ≥ 2.0, `OPENAI_API_KEY`). Same flags as the old script:
`--prompt --output --ref --edit --aspect --size --skip-existing`, plus `--quality --mask --transparent --n --model --no-fallback`.
A/B tool: `scripts/compare_image_models.py`.

## Models (updated 2026-09-11)

| `--model` | API id (snapshot) | Use it for | Status on our keys |
|---|---|---|---|
| `gpt-image-2` / `2` | `gpt-image-2` (`gpt-image-2-2026-04-21`) | previous default (until 2026-09-11); rollback + automatic fallback | ✅ live |
| `flare` | `gpt-image-2.5-flare` (`-2026-09-08`) | small 2.5 model: ≈ GPT Image 2 quality at up to 50 % lower latency → previs, storyboard coverage, variants | ✅ all three keys — Mac + Fastlane project and KontentPlus agency project (verified live 2026-09-11, `--no-fallback`) |
| **`sunburst` (default)** | `gpt-image-2.5-sunburst` (`-2026-09-08`) | 2.5 base model: higher quality than 2, most precise multi-turn edits and subject preservation → hero stills, video first frames, identity edits, label fixes | ✅ all three keys (verified live 2026-09-11) |

- Released 2026-09-08 with ChatGPT Images 2.5. Same token rates as GPT Image 2: $5/M text in, $8/M image in,
  $30/M image out (cached $1.25 / $2). Tier-1 limit 5 images/min on all three.
- 2.5 adds `quality` **`xhigh`** and **`max`** (default `auto`), `background` `auto|opaque|transparent`. The script maps
  `xhigh/max → high` if it has to run on gpt-image-2.
- Access can need **API Organization Verification** (platform.openai.com → Settings → Organization → General) and rolls
  out per project. Check: `curl -s https://api.openai.com/v1/models/gpt-image-2.5-flare -H "Authorization: Bearer $OPENAI_API_KEY"`.
- When a 2.5 model is not available the script prints a NOTE and falls back to `gpt-image-2`, so `--model sunburst` in a
  pipeline never breaks a run. `--no-fallback` makes it an error (use that when you are testing the model itself).
- **Default = `gpt-image-2.5-sunburst` since 2026-09-11** (Aman's decision after the A/B below). Override per call with
  `--model flare` (fast previs) or `--model 2` (GPT Image 2), or per machine with `GPT_IMAGE_MODEL=...` in `~/config.env`.

### Switching a workflow to 2.5 — OpenAI's migration procedure, applied to films

1. **Baseline set** (keep it in the project: `refs/ab/`): one candid Scandinavian-office still (photoreal), a character
   sheet → scene edit with 2 refs (identity), a product with exact label text, an archival era still, a UI-on-a-screen
   still, a transparent logo. Record model, settings, result.
2. **First candidate:** our GPT Image 2 stills already pass → start with **Flare** and look for the latency win. Where
   GPT Image 2 fell short (face drift across edits, label letters, "render" look) → start with **Sunburst** and first
   prove it fixes that.
3. **Same prompt, refs, size, quality, output format** for the first comparison — a quality label is not the same
   quality across models:
   `python scripts/compare_image_models.py --prompt "..." --ref refs/character.png --quality medium --runs 2 --out refs/ab/office`
4. **Judge the whole result:** instruction following, identity/product preservation, exact text, unwanted changes,
   alpha; repeat to see consistency; for edit chains test the full sequence, not one step.
5. **Then latency and $ per accepted image.** Tune one setting at a time (quality before prompt rewrites); try a lower
   quality once one passes; `xhigh`/`max` only when they fix a defect `high` leaves.
6. Keep `gpt-image-2` as rollback while it is supported.

## Endpoints the script uses

| Mode | When | API |
|---|---|---|
| generate | no `--ref` / `--edit` | `client.images.generate(model, prompt, size, quality, output_format, background, moderation, n)` |
| edit | any `--ref` or `--edit` (+ optional `--mask`) | `client.images.edit(model, image=[...], mask, prompt, ...)` — all refs are sent as `image[]`; `--edit` goes first |

Output is `b64_json` → written as png/jpeg/webp (from the output extension). Transparent backgrounds need png/webp.
Do not send `input_fidelity` to gpt-image-2 or 2.5 — inputs are always processed at high fidelity.
Masks are guidance, not a stencil: "the model uses the mask as guidance, but may not follow its exact shape".
Multi-turn edits in the Responses API (`previous_response_id`) exist; the script instead chains edits by passing the
previous output as `--edit`, which keeps every step on disk.

## Sizes

Max edge 3840 px, multiples of 16, ratio ≤ 3:1, 655,360–8,294,400 pixels; above 2560×1440 is experimental.

| `--aspect` | `--size 1K` | `2K` | `4K` |
|---|---|---|---|
| 16:9 | 1536×864 | 2048×1152 | 3840×2160 |
| 9:16 | 864×1536 | 1152×2048 | 2160×3840 |
| 3:2 / 2:3 | 1536×1024 / 1024×1536 | 2400×1600 | 3504×2336 |
| 1:1 | 1024×1024 | 2048×2048 | 2880×2880 |
| 21:9 | 1536×656 | 2048×880 | 3840×1648 |
| 4:3 / 3:4 | 1408×1056 | 2048×1536 | 3264×2448 |

Before 2.3.0 `--aspect 16:9 --size 1K` produced 1536×1024 (really 3:2) and the 4:3 / 3:4 "4K" presets exceeded the
8.29 MP limit. Use `--aspect 3:2` to reproduce old 1K stills exactly. Or `--size WxH`. For video first frames 1K is plenty (Omni/LTX/Seedance resample anyway); use 2K/4K for print,
packaging close-ups and end cards you will crop.

Cost: token-billed. Measured on Sunburst (default) at 1K: low ≈ $0.006 (~10 s), medium ≈ $0.01–0.02 (~15 s), high ≈ $0.033
(~29 s, ~1.1k output tokens). GPT Image 2 medium was ≈ $0.03–0.05 and ~30 s. The script prints tokens and estimated $ per call.
Rate limit tier 1 = 5 images/min — parallelize at most 4 stills at a time.

## Prompting GPT Image (2 and 2.5 — same fundamentals)

The 2.5 guide reuses the GPT Image 2 prompts word for word: **our existing prompts carry over unchanged** for the first
comparison. What the guide says, in the order that matters for films:

- **Define the result first:** subject + intended use (storyboard still, product photograph, end card). For complex
  requests use labelled sections: SCENE → SUBJECT → DETAILS → CONSTRAINTS. Any format works (paragraph, JSON-ish, tags) —
  pick the one that is easiest to maintain.
- **Photoreal:** say "photorealistic" / "real photograph". Camera specs are cues for look and framing, not physics. For
  wide, cinematic, low-light, rain or neon scenes name **scale, atmosphere and colour** — mood words alone make the
  model trade mood for surface realism.
- **People:** body framing, relative scale, gaze and object interaction ("full body visible, feet included", "looking
  down at the open book, not at the camera", "hands gripping the handlebars").
- **Text:** copy in quotes, position + typography, **how many times it appears** ("render the tagline exactly once"),
  "no extra text"; spell brand names letter by letter; medium/high for small or dense text. Still check every letter.
- **Edits:** "change only X" + the preserve list (identity, geometry, layout, lighting, labels; for surgical edits also
  saturation, contrast, camera angle, surrounding objects). Repeat the preserve list on every turn.
- **References by number and role:** "Image 1 is the character (keep the face identical), image 2 is the room (keep the
  layout)" and say which element moves where. Up to ~4 refs keeps fidelity high.
- **Iterate one change at a time:** pass the previous output as the next `--edit`, request one change, restate what
  stays. 2.5's headline gain is edit consistency across turns — use chains of small edits of ONE base still (the
  FLUX 3 keyframe trick in `learnings.md`) on Sunburst.
- **Pixel-identical regions:** if something must not move at all (a logo lock-up, a UI plate), composite the approved
  edit into the original with a mask (ffmpeg/PIL) instead of trusting the prompt.
- **Transparency:** `--transparent` + png/webp; ask for "an isolated subject on a fully transparent background, no
  backdrop, no checkerboard, no shadow"; open the file and check the alpha on hair, glass and shadows — a drawn
  checkerboard is not transparency.
- `--quality medium` for storyboard coverage, `high` for hero stills / anything that becomes a first frame.
- `--transparent` for logos and overlays destined for HyperFrames.
- Moderation: `--moderation low` only relaxes borderline filtering; real-person likeness of public figures is refused.

## Verified 2026-09-04 (gpt-image-2)

`--aspect 16:9 --size 1K --quality medium`: 1536×1024 product still with the label text "NORRA" rendered correctly,
38 s, 54 input / 1372 output tokens. Used directly as the Omni first frame — composition preserved.

## A/B 2026-09-11 — GPT Image 2 vs 2.5 Flare vs 2.5 Sunburst on film stills (medium, same prompt/size)

`compare_image_models.py`, 4 cases, one run per cell, Fastlane key (prompts in the session's `ab_suite.sh`):

| Case | gpt-image-2 | 2.5 Flare | 2.5 Sunburst | Verdict |
|---|---|---|---|---|
| Candid Scandinavian office (t2i, 16:9) | 31 s · $0.033 — good, but a Paris-style window | 12 s · $0.009 — Stockholm skyline, post-its on the monitor edge as asked | 15 s · $0.009 — most "real photograph": doorway framing, pinned prints, spire outside | Sunburst > Flare > 2 |
| Product label, exact text (1:1) | 34 s · $0.053 — all 3 lines exact | 9.5 s · $0.014 — exact, italic serif, negative space left as asked | 16 s · $0.014 — exact, cleanest light serif, best label typography | Sunburst ≥ Flare ≥ 2 |
| 1966 archival boardroom (t2i) | 32 s · $0.033 — convincing | 13 s · $0.009 — convincing, Stockholm skyline | 16 s · $0.009 — convincing, City Hall skyline, negative scratches as asked | all usable; 2.5 more specific |
| Edit: same office → evening (`--edit`) | 29 s · $0.043 — layout kept, lamp barely lights her | 13 s · $0.019 — layout + identity kept, warm lamp light on face and desk | 16 s · $0.019 — layout + identity kept, subtler, most natural light | 2.5 > 2 |

Take-aways: both 2.5 models were 2–3.6× faster and ~¼–⅓ of the cost per image (far fewer output tokens at the same
`medium`) with equal or better adherence and identity preservation. **Recommendation:** Flare for previs / storyboard
coverage / variants, Sunburst for hero stills, first frames and label shots — Sunburst costs the same as Flare here and
is only ~3 s slower. Keep gpt-image-2 as rollback. → Aman made Sunburst the default the same day. Access flapped for ~20 min after the models were enabled (the same key got 200 on one call and
`model_not_found` on the next) — the script's fallback covers that window.

## Photorealism stack (learned on the KontentPlus intro, 2026-09-04)

Default output leans "showroom render": symmetrical, spotless, glossy. OpenAI's own prompting guide and our tests
agree on the fix:

1. Say **"photorealistic"** and **"a real photograph taken on a real camera"** explicitly — these words switch modes.
2. Structure the prompt **SCENE → SUBJECT → DETAILS → CONSTRAINTS → USE** (labelled segments debug better than a paragraph).
3. Camera language is for *composition and mood*, not physics: "handheld from the doorway, slightly off-axis, 35mm, f/2,
   ISO 1600, natural available light". Specs are interpreted loosely; the framing intent lands.
4. **Ask for imperfections**: cable clutter, a coffee ring, post-its, uneven frames, dust in the lamp light, pilling
   knitwear, pores. "Documentary commercial look, not a 3D render, not a showroom, not symmetrical."
5. Avoid render vocabulary ("octane", "8k", "concept art", "hyper-detailed") and stock-photo words ("stunning", "beautiful").
6. For people: "honest and unposed, real skin texture, no retouching" and give them something to do or a thought.
   State the gaze ("eyes on the screen, not at the camera").
7. Reference images: name each by index and role ("Image 1 is the set reference photograph — keep every object where it is").
8. Offices (house style): Scandinavian — white or black sit-stand desks on black frames, black mesh chairs, white walls,
   light-grey floor, one plant. No brown wood. `--quality high` for identity-sensitive frames.

Set references made this way stayed consistent across night/day variants and worked as `--ref` inputs.

# Inspiration & Reference Analysis (Step 0 of every film)

The single highest-leverage thing in AI film production is **analyzing a real reference before generating anything**
(see `learnings.md` → "Reference Ad Analysis Workflow": the Chanel 25 breakdown told us to never shoot the CC lock in
macro, keep the bag at 10–15 % of frame, and cut every 2–3 s). `scripts/analyze_reference.py` makes that repeatable and
turns one or more inspiration videos into a **production brief with copy-paste prompt blocks and a shot plan**.

## What it does

1. **Ingests** local files, YouTube URLs (streamed straight to Gemini — no download), or other video URLs (`yt-dlp`).
2. **Measures** hard cuts with ffmpeg (`scene>0.3`) and writes a contact sheet of every shot (local files only).
3. **Analyzes** with Gemini video understanding (`gemini-3.8-flash`, fallbacks `gemini-3.5-flash`, `gemini-2.5-flash`):
   structure (hook/setup/build/payoff/CTA), full shot list with sizes/moves/light/color/product framing, pacing
   stats, palette hexes, camera vocabulary, product strategy, talent usage, audio, typography, techniques, and an
   **AI-generation risk** per shot (fluids, logos, hands, crowds, text-in-scene).
4. **Emits prompt blocks**: `STYLE_LOCK` (paste into every image/video prompt), `CAMERA_VOCAB`, `PACING_TARGET`,
   `AUDIO_DIRECTION`, `SHOT_TEMPLATE`.
5. **Fuses** several references + your goal into `brief.md`: style DNA, target spec, shot plan with a recommended
   model per shot (Omni / LTX / Seedance / still+Ken Burns), image + video prompt seeds, the consistency locks you
   must write in Step 1, risks, and a **do-not-copy** list (brand-specific assets).

```bash
source ~/config.env   # GEMINI_API_KEY

python3 scripts/analyze_reference.py \
    --input "https://www.youtube.com/watch?v=ohvN6A7Onos" \      # a campaign film
    --input refs/competitor_reel.mp4 \                            # a local file
    --goal "30s vertical product promo for NORRA face serum, Instagram Reels, no faces in close-up" \
    --brand NORRA \
    --output refs/analysis
```

Outputs in `refs/analysis/`: `<name>.json`, `<name>.md`, `<name>_cuts.json`, `<name>_contact.png`, `brief.json`, `brief.md`.

Flags: `--sample-fps 2` for fast-cut ads (default 1 fps; 0.5 for long films — cheaper), `--scene-threshold 0.2..0.5`,
`--extra "focus on how the product is lit"`, `--skip-existing` to reuse a previous analysis and only re-fuse the brief,
`--model gemini-3.8-flash`.

Cost: a 60 s ad ≈ 20–40k input tokens on Flash — cents. YouTube URLs: public videos only, free tier caps at 8 h/day.
Files API: up to 2 GB / 90 min per file. Uploaded files expire after 48 h.

## How to use the outputs in the pipeline

| Output | Feeds |
|--------|-------|
| `brief.md` → **STYLE_LOCK** | Every `generate_image_gpt.py` and video prompt (right after the character/set lock blocks) |
| **PACING_TARGET** / `shot_plan.duration_s` | `--clip path:seconds` in `build_hyperframes_timeline.py`; how much of each 6–8 s generation you keep |
| **CAMERA_VOCAB** | The `[CAMERA]` slot of each video prompt — one move per clip |
| `shot_plan.recommended_model` | Which of `generate_video_omni.py` (Omni) / `generate_video_ltx.py` / `generate_video_seedance.py` to call |
| `shot_plan.image_prompt_seed` | Storyboard still prompts for GPT Image 2 (Step 3) |
| `consistency_locks_needed` | Which Character / Set / Prop Lock Blocks to write (Step 1) |
| **AUDIO_DIRECTION** | `generate_music.py --prompt`, `generate_sfx.py`, VO delivery settings |
| **TYPOGRAPHY** | Title/end-card styling in `index.html` (edit the generated CSS) |
| `do_not_copy` | Guardrail — never reproduce these; the brief already abstracts the craft away from the brand |
| `ai_generation_risk: high` shots | Re-plan the beat: medium distance instead of macro, hands out of frame, no pouring/dispensing, typography in post |

Show the user `brief.md` and the contact sheet(s) and get sign-off **before** writing the script. It is a cheap gate:
the whole analysis costs less than one failed video generation.

## Reference video as a *generation input* (not just analysis)

Seedance 2.5 accepts up to **10 reference videos** (`--ref-video`, roles `reference_video`) and replicates their
camera move / choreography / rhythm — "camera like @Video1, cut rhythm like @Video2". Pair with the analysis: cut the
1–3 most useful shots out of the inspiration with ffmpeg (`-ss/-t`), keep them ≤ 30 s total, and pass them as refs.
LTX `audio-to-video` does the equivalent for music-driven cuts. Use the inspiration's *craft*, never its footage or
talent in the output.

## Prompting the analysis for specific genres

- **Ad / product promo** (default prompt is tuned for this): product screen time, first reveal, hero moment, CTA timing.
- **Short film / narrative**: add `--extra "Also map the emotional arc per shot and note dialogue vs. silence"` and `--sample-fps 0.5`.
- **Music video / beat-driven**: add `--extra "Mark every cut relative to the beat grid and count cuts per bar"` and `--sample-fps 2`; then `npx hyperframes beats` on your own track.
- **UGC / talking head**: `--extra "Describe framing, lens, captions style and hook copy verbatim"`.

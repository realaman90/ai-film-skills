---
name: ai-film-studio
description: |
  AI film production studio with pre-built scripts: analyze inspiration/reference videos (Gemini), write script + storyboard, generate stills (GPT Image 2; Seedream 5 / Nano Banana as fallbacks), video (Gemini Omni 1.1 Flash, FLUX 3 Video, Seedance 2.5/2.0, LTX 2.5/2.3; Veo 3.1 fallback), audio (ElevenLabs), and assemble the final cut with HyperFrames (HTML→MP4; replaced Remotion) or ffmpeg.
  Use when: creating short films, ads, product promos, brand films, social reels, storyboards, video scenes, voiceovers, music, sound effects, or any AI-powered media creation — especially "make one like this reference video".
  Trigger words: film, movie, video, ad, commercial, promo, product video, reel, storyboard, animate, scene, voiceover, narration, soundtrack, clip, short film, inspiration video, reference video.
user-invocable: true
metadata:
  author: realaman90
  version: "2.2.0"
  homepage: "https://github.com/realaman90/skills"
---

# AI Film Studio

End-to-end AI film production. The agent handles the creative decisions (reference analysis, story, prompts, pacing);
pre-built scripts handle the API plumbing. Works for **short films, ads, product promos, brand films and social reels** —
the pipeline is the same, only Step 0 (inspiration) and the assembly template (end card, CTA, aspect) change.

## Intake — route before you generate anything

Classify the deliverable first. Only the last two rows need generative video models; everything else is HyperFrames alone.

| The user wants… | Route | Why |
|---|---|---|
| **Motion graphics only** — kinetic type, logo sting, stat count-up, chart, lower-third, animated headline/tweet, transparent overlay (usually < 15 s, no footage) | `/motion-graphics` (official HyperFrames workflow skill; if missing: `npx hyperframes@0.8.27 skills update motion-graphics`) | zero generation cost; deterministic, editable HTML |
| A promo/site tour from a **website URL** | `/product-launch-video` | captures the real site; no AI footage needed |
| A narrated **explainer from text/notes**, no URL | `/faceless-explainer` | HyperFrames generates its own visuals |
| **Existing footage** that needs captions or graphic packaging | `/embedded-captions` (subtitles) · `/talking-head-recut` (titles, lower-thirds, callouts) | footage untouched |
| A **deck / presentation** | `/slideshow` | navigable deck, not a render |
| **Beat-synced cut of images/clips to a music track** | `/music-to-video` | beat grid drives the edit |
| **Film / ad / promo / reel with generated footage** | this skill, Steps 0–7 | needs stills + video models |
| **Hybrid**: generated plates *plus* heavy graphics (kinetic type over AI footage, data callouts, shader transitions) | Steps 0–5 here for the clips, then `/hyperframes-animation` blueprints + `/hyperframes-core` instead of `build_hyperframes_timeline.py` | the simple timeline builder only does cards, overlays, captions and crossfades |

Rules of thumb:
- If no shot needs *photographed-looking* content, do not open a video model. Type, shapes, charts and logos are HyperFrames' job.
- **Diegetic vs. graphic.** Omni/Seedance may render effects that live *inside* the footage (smoke forming a shape, light writing a word, particles becoming a product). Anything that must be exact and editable — brand typography, prices, claims, CTAs, captions, lower-thirds — is composited in HyperFrames, never generated. Video-model text drifts frame to frame and cannot be fixed afterwards.
- Workflow skills (`motion-graphics`, `product-launch-video`, `faceless-explainer`, `embedded-captions`, `talking-head-recut`, `slideshow`, `music-to-video`, `general-video`, `media-use`) install **on demand**: `npx hyperframes@0.8.27 skills update <name …>` (the core `hyperframes-*` set alone does not include them). Check with `ls ~/.claude/skills`.
- When routing to an official HyperFrames skill, hand over the brief (product, duration, aspect, brand colours/fonts, any `STYLE_LOCK` from Step 0) and let that skill run its own loop (`init → lint → check → preview → render`). Come back here only if it turns out real footage is needed.
- Unsure? Ask one question: *"Does this need any footage of real-looking things, or is it graphics and text?"*

## Quick Reference

| Task | Tool |
|------|------|
| **Analyze inspiration video(s) → brief + shot plan** | `python scripts/analyze_reference.py --input ref.mp4 --input "https://youtube.com/..." --goal "30s 9:16 promo for X" --brand X --output refs/analysis` |
| Check available Gemini models | `python scripts/list_models.py [--filter image\|video]` |
| **Generate storyboard still (GPT Image 2)** | `python scripts/generate_image_gpt.py --prompt "..." --output scene.png [--aspect 9:16] [--size 2K] [--quality high]` |
| Still with character + set refs | `python scripts/generate_image_gpt.py --prompt "Image 1 = character, image 2 = room ..." --ref char.png --ref set.png --output scene.png` |
| Inpaint / edit a still | `python scripts/generate_image_gpt.py --prompt "..." --edit src.png [--mask m.png] --output out.png` |
| Transparent logo / overlay | `python scripts/generate_image_gpt.py --prompt "..." --aspect 1:1 --transparent --output logo.png` |
| Still via Seedream 5 (BytePlus; feeds Seedance faces) | `python scripts/generate_image_byteplus.py --prompt "..." --output scene.png` |
| Still via Nano Banana (fallback) | `python scripts/generate_image_gemini.py --prompt "..." [--model pro] --output scene.png` |
| **Video from still (Gemini Omni)** | `python scripts/generate_video_omni.py --prompt "..." --image scene.png --duration 6 --output scene.mp4` |
| Omni first + last frame / subject refs | `--image start.png --last-frame end.png` · `--ref char.png --ref prop.png` (address as `<IMAGE_REF_0>`) |
| Omni draft → upscale / extend / edit | `--resolution 360p` then `--upscale draft.mp4 --resolution 4k` · `--extend clip.mp4` · `--edit clip.mp4` · `--previous <id>` |
| Video via Veo 3.1 (fallback) | `python scripts/generate_video_veo.py --prompt "..." --image scene.png --output scene.mp4` |
| Video (LTX 2.3 fast, cheapest iteration) | `python scripts/generate_video_ltx.py --prompt "..." --image scene.png --output clip.mp4` |
| Video (LTX 2.5, newest look, 6–20 s) | `python scripts/generate_video_ltx.py --ltx-model ltx-2-5-fast --prompt "..." --image scene.png --output clip.mp4` |
| LTX: extend / retake a clip (2.3 pro) | `--endpoint extend --video clip.mp4 --duration 5` · `--endpoint retake --start-time 2 --duration 3` |
| LTX: audio-to-video (music-driven) | `--endpoint audio-to-video --audio music.mp3 --image scene.png` |
| **Video (FLUX 3: 5–20 s, dialogue + lip-sync, multi-shot in one take)** | `python scripts/generate_video_flux.py --prompt "Use this image as the first frame. ..." --image scene.png --duration 8 --output clip.mp4` |
| FLUX 3: draft → enhance (⅓ cost, same seed) | `--draft --output drafts/a.mp4` then `--enhance drafts/a.mp4 --resolution fhd --output clips/a.mp4` |
| FLUX 3: last frame / timed keyframes / continue / upscale | `--last-frame end.png` · `--mid-image b.png` (evenly spaced) · `--keyframe 4.5:mid.png` (timed) — ≤10 images, 3+ need `--duration` · `--video clip.mp4` (v2v, +5–15 s) · `--upscale clip.mp4 --upscale-factor 2` |
| Video (Seedance 2.0, products / 3D chars) | `python scripts/generate_video_seedance.py --prompt "..." --image scene.png --output clip.mp4` |
| **Video (Seedance 2.5: 30 s, 50 refs, ref videos)** | `python scripts/generate_video_seedance.py --model 2.5 --duration 30 --image p.png --ref-video move.mp4 --task-type reference --prompt "... like @Video1" --output ad.mp4` |
| Seedance 2.5: edit / extend a clip | `--model 2.5 --task-type edit --ref-video clip.mp4 --prompt "Video edit: remove ..."` · `--task-type extend --prompt "Extend @Video1 ..."` |
| Voiceover | `python scripts/generate_tts.py --text "..." --output vo.mp3 [--timestamps subs.json]` |
| Music | `python scripts/generate_music.py --prompt "..." --duration 120 --output score.mp3` |
| Sound effect | `python scripts/generate_sfx.py --text "..." --duration 8 --output sfx.mp3` |
| **Pick the best take per slot (Gemini)** | `python scripts/pick_takes.py --slot "1920s print" takes/a.mp4 takes/b.mp4 --out picks.json` |
| **Quality gate — blind jury** | `python scripts/jury.py renders/cut.mp4 --brief "50 s launch film for X" --runs 2` (`--anchored prev.json --changes "..."` only to ask what moved) |
| Phrase times from VO timestamps | `python scripts/vo_words.py audio/vo_words.json --anchor "It runs" "strategy" "every channel"` |
| Measure UI boxes for overlays | `python scripts/measure_ui.py hero/screen.html --grep "INTERVIEWS"` |
| **Finals: conform / join / render+master / probe** | `scripts/master.sh conform in.mp4 out.mp4 [1920 1080] [1.18]` · `master.sh join out.mp4 a.mp4:2.2 b.mp4:5.5` · `master.sh render film renders/final.mp4` · `master.sh probe final.mp4` |
| Spend estimate from disk | `python scripts/cost_report.py /path/to/project` |
| Probe media | `python scripts/probe.py clips/ --format table` |
| Assemble (ffmpeg, fast, no graphics) | `python scripts/assemble.py --videos-dir clips/ --narration vo.mp3 --music score.mp3 --output film.mp4` |
| **Scaffold HyperFrames project** | `scripts/new_hyperframes_project.sh /tmp/my-film/film --aspect 9:16` |
| **Build timeline (index.html + scenes.json)** | `python scripts/build_hyperframes_timeline.py --project /tmp/my-film/film --clip assets/clips/a.mp4:3 --title "Intro\|2" --end-card "brand.com\|3:cta=Shop now" --music assets/audio/bgm.mp3 --voiceover assets/audio/vo.mp3 --logo assets/images/logo.png` |
| Validate composition | `(cd /tmp/my-film/film && npx --yes hyperframes@0.8.27 check)` |
| Snapshot frames (no render) | `scripts/snapshot_hyperframes.sh /tmp/my-film/film 0.5,4,9` |
| **Render final film** | `scripts/render_hyperframes.sh /tmp/my-film/film renders/film.mp4 [--quality draft] [--format gif]` |
| Prompting: images | [reference/gpt-image.md](reference/gpt-image.md) · [reference/seedream.md](reference/seedream.md) · [reference/nano-banana.md](reference/nano-banana.md) (fallback) |
| Prompting: video | [reference/omni.md](reference/omni.md) · [reference/flux3.md](reference/flux3.md) · [reference/flux3-camera.md](reference/flux3-camera.md) (camera & style vocabulary) · [reference/ltx.md](reference/ltx.md) · [reference/seedance.md](reference/seedance.md) · [reference/veo.md](reference/veo.md) (fallback) |
| Voice / music / SFX | [reference/elevenlabs.md](reference/elevenlabs.md) |
| **Inspiration analysis guide** | [reference/inspiration.md](reference/inspiration.md) |
| **HyperFrames assembly guide** | [reference/hyperframes.md](reference/hyperframes.md) |
| **Worked prompt examples per model + production shapes** | [reference/examples.md](reference/examples.md) — official Omni/Veo/Seedance/LTX examples, UGC one-shot template, asset-lock commercial, keynote choreography, ad timing rules |
| Hard-learned lessons | [reference/learnings.md](reference/learnings.md) |
| **Worked example (50 s B2B launch film, 16:9 + 9:16)** | [examples/kontentplus-intro/](examples/kontentplus-intro/README.md) — spec/overlay scripts, VO-driven timing, native product canvas, era-footage picker, jury logs, cost |

**All scripts require `source ~/config.env` first.** If not found, ask the user where it is (never guess or print key values).
Tip: keep the real keys in one gitignored `config.env` (e.g. inside your clone of this repo) and make `~/config.env` a small loader that sources it. `media_host.py` also accepts the alias names `S3_BUCKET_NAME`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` and `ASSET_STORAGE=s3|r2`; map any other aliases (e.g. `BYTEPLUS_ARK_API_KEY` → `ARK_API_KEY`, `LTX_API_KEY` → `LTXV_API_KEY`) in that loader.

Legacy Remotion template + scripts: `legacy/` (kept for old projects; `/remotion-to-hyperframes` ports compositions).

---

## Setup

```bash
source ~/config.env  # MUST run before any API call
pip install -r requirements.txt   # openai google-genai pillow requests boto3 yt-dlp
brew install ffmpeg               # macOS
node --version                    # 22+ for HyperFrames (npx fetches hyperframes@0.8.27 on first use)
```

`config.env` must define:
- `OPENAI_API_KEY` — OpenAI (GPT Image 2 stills)
- `GEMINI_API_KEY` — Google AI Studio (Omni video, **reference-video analysis**, Nano Banana / Veo fallbacks)
- `ELEVENLABS_KEY`, `ELEVENLABS_VOICE` — ElevenLabs (voice, music, SFX)
- `ARK_API_KEY` — BytePlus Ark (Seedance 2.5/2.0, Seedream 5)
- `LTXV_API_KEY` — LTX (Lightricks)
- `BFL_API_KEY` — Black Forest Labs (FLUX 3 Video; https://dashboard.bfl.ai). Local files go inline as base64, no S3 needed.
- `S3_BUCKET`, `S3_REGION` (+ optional `S3_PUBLIC_URL`, `S3_PREFIX`) — Amazon S3; hosts local images/videos as URLs for Seedance/Seedream (`scripts/media_host.py check` to verify). Standard `AWS_*` credentials or `AWS_PROFILE`.

---

## Film Production Workflow

```
0. Inspiration      analyze_reference.py  →  refs/analysis/brief.md   (STYLE_LOCK, pacing, shot plan, model per shot)
1. Script           script.md + scenes.md + lock blocks (character / set / props)
2. References       refs/*.png (character sheet, set wide, set detail)   ← approve
3. Storyboard       storyboard/scene_NN.png with all refs attached        ← approve (gate!)
4. Clips            clips/scene_NN.mp4 (Omni / LTX / Seedance per brief) → clips/cfr/
5. Audio            audio/vo.mp3 (+ subs.json), bgmusic.mp3, sfx/
6. Assemble         HyperFrames project → check → snapshot → render   (product beats NATIVE, see §Product sections)
7. Review           watch, fix, re-render; blind jury.py as the gate (twice); stop when its notes turn structural
8. Finals           master.sh: HD conform → high-quality render → −14 LUFS → faststart; 9:16 from the same build
```

### Step 0: Inspiration & Reference Analysis (do this first)

Ask for (or find) 1–3 reference videos the user admires in the same category — a competitor ad, a brand film, a
reel. Then:

```bash
python scripts/analyze_reference.py \
    --input "https://www.youtube.com/watch?v=..." --input refs/competitor.mp4 \
    --goal "30s vertical product promo for NORRA face serum, Instagram Reels, no faces in close-up" \
    --brand NORRA --output refs/analysis
```

You get per-video shot lists + contact sheets and a fused **`brief.md`**: STYLE_LOCK (paste into every prompt),
PACING_TARGET, CAMERA_VOCAB, AUDIO_DIRECTION, TYPOGRAPHY, a **shot plan with a recommended model per shot** and
prompt seeds, the consistency locks you need, risks, and a do-not-copy list. Show the brief + contact sheets to the
user and get sign-off before writing the script. Details: [reference/inspiration.md](reference/inspiration.md).

No reference available? Skip to Step 1 but still write a STYLE_LOCK by hand (medium, lens, grade, light, palette).

### Step 0.5: Directing gates — read `reference/directing.md` before Step 1

No still before the concept is locked in words, no video before the shot list is approved. Four gates: **G0** brief
reflected back → **G1** one concept locked (spine, but/therefore, wound/stakes/turn, ending first) → **G2** timed beat
sheet with value shifts and an *audience-knowledge ledger* (every fact the ending needs is planted on screen earlier)
→ **G3** shot list with a reason for every camera move and a 30–50-word **identity string** per character, pasted
verbatim into every prompt from here on. Prompts name bodies and objects, never emotions or "cinematic". When a
take fails, name the failure code and climb the cost ladder (prompt edit → parameter → regenerate → keyframe →
re-plan → fix in the edit). The vendored source skills are in `vendor/` (see `vendor/VENDOR.md`).

#### The director's sheet (Gates 2–3 as one reviewable page)

Once the beat sheet exists, turn it into a **plan file** and a review page, and stop until the reviewer has decided
every scene. Non-directors approve better from a sheet than from a chat thread.

```bash
# plan.json: title, spine, acts, cast (identity strings, sheet images), scenes (purpose, what-the-audience-learns,
# value shift, coverage table, dialogue native+en, continuity, previs image key) — schema in scripts/director_sheet.py
python3 scripts/director_sheet.py build --plan v3/sheet/plan.json --out v3/sheet/sheet.html --images v3/previs v2/refs
```
- Previs: one still per scene (GPT Image 2, 1K medium, cast sheets as `--ref`, the first wide shot as the prompt) so the
  reviewer sees *how it will appear*; put them in an images dir as `previs_<sceneId>.jpg`.
- **In Claude Code:** publish `sheet.html` with the Artifact tool and `capabilities: {db: {}}`. Approvals and notes are
  stored per scene in the artifact db (collection `reviews`, doc id = scene id). Read them back with
  `read_db` (db_op `list`, collection `reviews`), save as `v3/sheet/decisions.json`, then
  `python3 scripts/director_sheet.py decisions --plan … --decisions …` prints the retake/rewrite list and says whether
  Gate 3 is open.
- **Outside Claude Code** (a client, a teammate with the HTML file): the same page works from a file or any host; the
  reviewer presses **Copy decisions as JSON** and sends it back; save that text as `decisions.json`. No server needed.
- Rule: no video generation until `decisions` reports every scene approved. Scenes marked *needs changes* go back to
  the beat sheet, not to the prompt.

### Step 1: Script & Scene Breakdown

Write the narration/dialogue script (≈2.5 words/s for VO). Break into scenes: `| Scene | Time | Duration | Setting |
Action | Camera | Mood | VO |`. Durations come from the brief's PACING_TARGET (ads: 2–3.5 s per shot, hook by 2 s;
films: 4–8 s). For **ads/promos** add: product first-reveal time, hero moment, end card + CTA copy, logo placement.

Define **lock blocks** — identical text pasted into every relevant prompt:

**Character Lock Block** (one per recurring character):
```
TAKESHI (old) -- Elderly Japanese man, late 70s, thin white hair swept back,
wire-rimmed round spectacles, gentle weathered face. Worn dark brown wool vest
over cream linen shirt, leather work apron with tool pockets.
```

**Set Lock Block** (one per recurring location, with LEFT/RIGHT positions, surfaces, walls, light sources):
```
WORKSHOP -- Traditional Japanese clock repair workshop. Wooden workbench against
back wall, single oil lamp on the LEFT side of bench. Walls floor-to-ceiling with
clocks: 3 grandfather clocks on the LEFT wall, rows of pendulum clocks above the bench,
pocket watches on hooks to the RIGHT. Window on the LEFT wall. Scattered brass gears,
tweezers, magnifying loupe, small brass bird near the RIGHT edge of the bench.
```

**Product Lock Block** (ads): exact object, materials, finish, label text, what must NOT change, and the framing rule
from the brief (e.g. "product at 10–15 % of frame, never macro on the pump/logo").

### Step 2: Reference Images

```bash
# Character sheet (1:1, clean background)
python scripts/generate_image_gpt.py --prompt "Character reference sheet. Front-facing portrait of: [CHARACTER LOCK]. Neutral background." --output refs/character.png --aspect 1:1 --quality high
# Set wide + set detail
python scripts/generate_image_gpt.py --prompt "[STYLE_LOCK] [SET LOCK]. Wide establishing shot of the full room. Set reference — every object position must be remembered." --output refs/set_wide.png
python scripts/generate_image_gpt.py --prompt "[STYLE_LOCK] Close-up of the workbench surface from [SET LOCK]. Prop reference." --output refs/set_detail.png
# Product: prefer the brand-approved still; if regenerating, --edit product.png (+ --mask) preserves geometry; GPT Image 2 renders label text reliably (quote it)
```

**Review and approve ALL references before generating any scene stills.**

### Step 3: Storyboard Stills

One still per scene, passing every relevant ref (character + set + product, up to 4):
```bash
python scripts/generate_image_gpt.py \
    --prompt "Image 1 is the character (keep the face identical), image 2 is the set (keep the layout). [STYLE_LOCK] [CHARACTER LOCK] [SET LOCK] [SCENE: shot size, camera, action, light]" \
    --ref refs/character.png --ref refs/set_wide.png \
    --output storyboard/scene_02.png --aspect 9:16 --quality medium
```
Generate 3–4 in parallel (background processes). Build a contact sheet and **show the user**:
```bash
ffmpeg -y -i storyboard/scene_%02d.png -filter_complex "scale=480:-1,tile=4x3:margin=4:padding=4" storyboard/contact_sheet.png
```
Consistency checklist: same face / same room layout / same props / same light direction / same palette across scenes.
**Do not generate video until ALL stills are approved.** (Stills cost cents; clips cost dollars.)

### Step 4: Video Clips

Pick the model per shot (the brief already suggests one):

| Feature | Gemini Omni 1.1 Flash | FLUX 3 Video | Seedance 2.5 | Seedance 2.0 | LTX 2.5 | LTX 2.3 |
|---------|------------------------|--------------|--------------|--------------|---------|---------|
| Provider | Google (`generate_video_omni.py`) | Black Forest Labs (`generate_video_flux.py`) | BytePlus Ark (`--model 2.5`) | BytePlus Ark (`--model full/fast/mini`) | LTX (`--ltx-model ltx-2-5-*`) | LTX (`--ltx-model ltx-2-3-*`) |
| Photoreal human faces | ✅ | ✅ | ❌ blocked (Seedream 5 workaround) | ❌ blocked | ✅ | ✅ |
| Duration | 3–10 s (+extend to 40 s) | **5–20 s** (+5–15 s per continuation) | **4–30 s** | 4–15 s | 6–20 s (fast) / 6–10 s (pro) | 2–20 s |
| Max resolution | 4K (upscaled from 720p) | 1080p (`fhd` upsampler) · `--upscale` ×3 | 1080p 10-bit | 4K | 4K (fast) | 4K |
| First + last frame | ✅ | ✅ + up to 10 timed keyframes | ✅ | ✅ | ✅ | ✅ |
| Reference videos (motion/camera) | ✅ 3 × ≤3 s | ❌ (continuation only) | **✅ up to 10** | ✅ 3 | ❌ | ❌ |
| Extend / edit | ✅ extend + conversational edit + `--previous` | continue (v2v) · draft → enhance (same seed) · no edit | edit + extend | edit + extend | ❌ | retake/extend (pro) |
| Multi-shot in one generation | one continuous shot | **✅ `SHOT N: … HARD CUT.`** | time-coded beats | time-coded beats | 2–3, less reliable | 2–3, less reliable |
| Audio | built-in | built-in, **dialogue + lip-sync 13+ languages** | `generate_audio` | `generate_audio` | built-in | built-in |
| Cost / 8 s (approx.) | $0.24 (360p) · $0.80 (720p) · $1.20 (1080p) | $0.48 (draft) · $1.36 (hd) · $2.32 (fhd) | ~$1.2 | ~$1.0 | ~$0.7–1.2 | ~$0.25 |
| Best for | hero shots with people, 360p drafts → 4K, fixing a take by talking to it | dialogue scenes, multi-shot sequences, era/doc formats, storyboard keyframes | 30 s one-shot ads, "camera like @Video1", 3D chars, products | products, motion refs | newest look, long takes | cheap iteration, faces, retakes |

Veo 3.1 is still wired up as a fallback (`generate_video_veo.py`, see [reference/veo.md](reference/veo.md)). Routing rule of thumb: a shot
with **talking** or **more than one angle** → FLUX 3; a hero shot you will iterate by feel → Omni; a 30 s product one-take with a motion
reference → Seedance 2.5; coverage at scale or a fix inside a clip → LTX. Details: [reference/flux3.md](reference/flux3.md).

```bash
# Most scenes: image-to-video, prompt = ONLY [CAMERA] + [ACTION] + [LIGHT CHANGE] + [AUDIO]; the still carries the look
python scripts/generate_video_ltx.py --prompt "Camera holds. The rim light breathes brighter over six seconds. Quiet room tone." --image storyboard/scene_01.png --output clips/scene_01.mp4
python scripts/generate_video_omni.py --prompt "In a single continuous shot, slow dolly forward. Ambient: crickets, water. No music." --image storyboard/scene_02.png --duration 6 --output clips/scene_02.mp4
# FLUX 3: dialogue scene from a still — draft at ⅓ cost, then enhance the keeper (same generation, no re-roll)
python scripts/generate_video_flux.py --prompt "Use this image as the first frame. Camera locked at eye level, 70 mm, shallow focus. After a beat she looks up and says, quiet and warm, 'Try it now.' Ambience: rain on the window, a clock tick. No music, no on-screen text, no subtitles." --image storyboard/scene_04.png --duration 8 --draft --output drafts/scene_04.mp4
python scripts/generate_video_flux.py --enhance drafts/scene_04.mp4 --resolution fhd --output clips/scene_04.mp4
# Omni draft loop: 360p first, refine by talking to it, then upscale the keeper
python scripts/generate_video_omni.py --prompt "..." --image storyboard/scene_03.png --resolution 360p --output drafts/scene_03.mp4
python scripts/generate_video_omni.py --previous <id from the run above> --prompt "Slower camera, keep everything else the same" --resolution 360p --output drafts/scene_03_v2.mp4
python scripts/generate_video_omni.py --upscale drafts/scene_03_v2.mp4 --resolution 1080p --output clips/scene_03.mp4
# Seedance 2.5: whole 30 s ad in one shot with the inspiration's camera move as a reference video
python scripts/generate_video_seedance.py --model 2.5 --duration 30 --ratio 9:16 --task-type reference \
    --image refs/product.png --ref-video refs/analysis/_cuts/lateral_track.mp4 \
    --prompt "[STYLE_LOCK] Product like @Image1, camera move like @Video1. 0-3s ... 3-8s ... " --output clips/ad_oneshot.mp4
```
Then **convert every clip to CFR** and trim to the best 2–3.5 s for ads (AI clips are strongest in their first seconds):
```bash
mkdir -p clips/cfr && for f in clips/*.mp4; do ffmpeg -y -i "$f" -r 24 -vsync cfr -c:v libx264 -preset fast -crf 18 -c:a aac "clips/cfr/$(basename "$f")"; done
```
Review each clip (thumbnail strip): face/product match, camera executed, no jitter, physics OK. Regenerate failures.

### Step 5: Audio

```bash
python scripts/generate_tts.py --file script.txt --output audio/vo.mp3 --speed 0.95 --timestamps audio/vo_subs.json
python scripts/generate_music.py --prompt "[AUDIO_DIRECTION from brief — style only, no artist names]" --duration 40 --output audio/bgmusic.mp3
python scripts/generate_sfx.py --text "glass pipette click, viscous drop" --duration 3 --output audio/sfx/drop.mp3
# Subtitles from the FINAL vo file (never reuse old timestamps):
whisper audio/vo.mp3 --model base --output_format json --word_timestamps True --output_dir audio/
```
Make the music **at least as long as the film** (the builder warns if not).

### Step 6: Assemble with HyperFrames

```bash
scripts/new_hyperframes_project.sh /tmp/my-film/film --aspect 9:16
cp clips/cfr/*.mp4 /tmp/my-film/film/assets/clips/ && cp audio/*.mp3 /tmp/my-film/film/assets/audio/ && cp refs/logo.png /tmp/my-film/film/assets/images/

python scripts/build_hyperframes_timeline.py --project /tmp/my-film/film \
    --title "NORRA|1.5:sub=Skin, simplified" \
    --clip "assets/clips/scene_01.mp4:3:text=Made for mornings" \
    --clip assets/clips/scene_02.mp4:2.5:trim=1.0 \
    --clip assets/clips/scene_03.mp4:3:audio=1 \
    --end-card "norra.se|3:cta=Shop the serum" \
    --music assets/audio/bgmusic.mp3 --music-volume 0.15 \
    --voiceover assets/audio/vo.mp3 --vo-offset 0.8 --subtitles audio/vo.json \
    --logo assets/images/logo.png --transition crossfade --transition-duration 0.4 --aspect 9:16 --fps 24

(cd /tmp/my-film/film && npx --yes hyperframes@0.8.27 check)      # lint + runtime + layout + motion + contrast
scripts/snapshot_hyperframes.sh /tmp/my-film/film 0.5,3,6,9        # look at PNGs before paying for a render
scripts/render_hyperframes.sh /tmp/my-film/film renders/draft.mp4 --quality draft
scripts/render_hyperframes.sh /tmp/my-film/film renders/film.mp4  # final
```

`scenes.json` next to `index.html` is the editable timeline (reorder, retime, add `"text"`, swap `"transition"`), then
`--spec scenes.json`. For anything the generator doesn't do (kinetic type, lower-thirds, shader transitions,
audio ducking, sub-compositions), hand-edit `index.html` following [reference/hyperframes.md](reference/hyperframes.md)
or invoke the official `/hyperframes` skills (installed globally). Quick, graphics-free cuts: `scripts/assemble.py` (ffmpeg).

### Step 7: Review & Iterate

Watch the render. Fix by layer: pacing → retime `scenes.json`; missing beat → generate/extend a clip (LTX extend,
Seedance 2.5 extend, FLUX 3 `--video` continuation); character/set drift → regenerate the still with the refs; audio → volumes in `scenes.json`; text →
edit `index.html`. Re-run `check`, snapshot the changed timestamps, re-render draft, then final.

## Product sections — build them natively, never as screenshots

Screenshots of an app with highlight rings read as slop and two rounds of them were rejected. What works:

- A **title scene with empty text** that your overlay script fills with real HTML: an agent log that checks off, a real
  post card with a generated photo, channel chips lighting up, a chart drawing with counters, a proposal being approved
  (blueprints: `agent-progress-theater`, `grid-card-assemble`, `constellation-hub`, `dataviz-countup` in
  `/hyperframes-animation`). One oversized world inside a camera wrapper (`transform-origin: 0 0`; to centre world
  point (wx, wy) at scale s: `x = FW/2 − wx·s, y = FH/2 − wy·s`) and pan between stations on the spoken words.
- Set `text-align: left; line-height: 1.25` on the injected root (title cards centre everything) and use the real logo
  mark in cards, never a coloured square.
- If a real screenshot plate must appear, **measure** its boxes (`measure_ui.py`) and map css → frame
  (`x·4/3, y·4/3 − 60` for a 1440×900 plate covered into 16:9); guessed ring coordinates were wrong three times out of three.
- Live-action cutaways after the interface break the "motion-first" flow for evaluators; if one is needed, bake the real
  product chart onto its screen (`generate_image_gpt.py --edit still.png --ref chart.png`) before animating it.

## Word-synced editing

Every era push, kinetic card and camera move lands on a spoken word, not on a guess:

1. `generate_tts.py --timestamps audio/vo_words.json` (character timestamps).
2. Schedule VO lines sequentially with a fixed gap; size each scene so the next anchored scene starts at
   `line.start − offset` (+ the transition overlap), clamped to the source length. Era offsets of −0.05 s make the push
   land *on* the line, not before it.
3. `vo_words.py --anchor "<line start>" "<phrase>"` gives the offset of a phrase inside a line → key tweens to
   `line.start + offset`. Long slots: join two takes with a hard cut so each phrase has its picture
   (`master.sh join`); slow a short take with `setpts` (1.18× is invisible on hand-cranked footage).
4. Music "hard stop" requests are ignored by the generator — build the stop in the mix (trim + silence + sub pulse +
   looped calm section).

## Archival / era footage that reads as real

`GPT Image 2 still → Omni image-to-video`, not text-to-video:

- Still prompt as an *authentic archival photograph*: name the process (glass plate, silver gelatin, Kodachrome, 35 mm
  consumer film + flash, camcorder), period clothing, **real faces** (Omni accepts them; Seedance rejects them in inputs),
  plate damage/grain/vignette, "no readable text, no modern objects".
- Omni prompt = era artefacts + **natural, moderate, continuous motion in one locked-off setup**: "no one enters or
  leaves, no new figures, hands keep their shape, no pans, no cuts". "Hold still" direction scores *lower* (frozen).
  Known failures: phantom figures after ~4 s (use the first 3 s), a whip-pan cut when two actions are listed, floating
  sci-fi UI when notifications are mentioned near a face, garbled text on generated screens.
- Two takes per slot → `pick_takes.py` (authenticity / motion / era / usability + artefact timestamps + best in-point).
- 720p drafts; finals via `--upscale` (the script refines the original interaction, which works from the EEA and is a
  true upscale). Conform with `master.sh conform` (crf 14, lanczos, 24 fps CFR).

## Quality gate — how to use the jury honestly

- Run `jury.py` **blind**, twice, with the explicit scale. Feeding it previous scores anchors it (it returned 7/10 for six
  rounds while calling every fix "improved"); use `--anchored` only to ask what moved.
- Blind Gemini tops out around 6–7 for generated plates; when its notes turn *structural* (a live-action cutaway
  after the UI, the tone at the turn) rather than about detail, more generations will not move it — say so and ship.
- Act on notes in this order: sync (pushes on lines) → product clarity (native beats) → B2B proof (pipeline, CPL,
  hours saved, an approve click) → end card (mark assembles, high-contrast CTA, risk-reversal line) → footage.

## Finals, masters and aspect variants

- `master.sh render <project> renders/final.mp4`: high-quality render → `loudnorm I=-14 TP=-1.5 LRA=11` → AAC 256k →
  `+faststart`; keep the `_raw` next to it. `master.sh probe` reports dims, fps, LUFS, true peak.
- Write overlays with `FW/FH` and helper `cx/cy` from day one; a `ASPECT=9:16 OUT_DIR=../film_916` switch (module
  60..1020 × 520..1060, axis at 1180, pushes ±FW, UI plates as cards with their own mapping, live action inside a
  module) turns the same build into the vertical cut. After any templating pass run
  `grep -o 'top:{F[HW][^"]*' index.html` — an unevaluated brace silently drops the element onto the class position.
- Cost: `cost_report.py <project>` before the client asks. A 50 s film with two footage rounds ran ≈ $65 in API spend
  (Seedance ≈ $30, Omni ≈ $22, stills ≈ $8, audio ≈ $4).
- Ask for the **tagline and real metrics at intake**; placeholders survive to the master otherwise.

---

## Film Types — what changes

| | Short film | Ad / commercial | Product promo / demo | Social reel |
|---|---|---|---|---|
| Length | 60–180 s | 6 / 15 / 30 s | 20–60 s | 7–30 s |
| Aspect | 16:9 | 16:9 + 9:16 cutdown | 16:9 or 9:16 | 9:16 |
| Shot length | 4–8 s | 2–3.5 s, hook ≤ 2 s | 3–5 s | 1.5–3 s |
| Step 0 refs | 1 film in the genre | 2–3 ads in the category | competitor demo + one brand film | 3 top reels |
| Must-have beats | arc: setup → tension → climax → resolution | hook, product reveal, hero moment, **end card + CTA + logo** | problem → product → proof → CTA | hook in first frame, caption-first, loopable end |
| Faces | Omni / FLUX 3 / LTX | often none (product) → Seedance 2.5 shines | hands only → Seedance / LTX | UGC feel → LTX + documentary prompt stack |
| Typography | title + credits | headline overlays, price/claim, CTA pill | feature callouts | burned-in captions (`--subtitles`) |
| Audio | VO + score + SFX | music-led, 1–2 VO lines, SFX hits on cuts | VO-led, light bed | music + captions, VO optional |
| Assembly | `--transition blur/dip`, fades | `--transition cut/crossfade 0.3`, `--end-card ...:cta=` | `--clip ...:text=` callouts | `--fps 30`, `--aspect 9:16`, `--fade-out 0` for loops |

Ads: also render the 16:9 master **and** a 9:16 cutdown (`--aspect 9:16` with re-framed stills or `--resolution`),
and a 6 s bumper from the hero shot + end card.

---

## Visual Consistency Rules

Three layers, each enforced by a reference image **and** a lock block in every prompt:

| Layer | What | How |
|-------|------|-----|
| Character | face, hair, clothes, build | character sheet `--ref` + Character Lock Block |
| Set / location | layout, walls, furniture, light direction, palette | set wide/detail `--ref` + Set Lock Block |
| Props / product | objects don't teleport; product geometry/label intact | detail `--ref` + Product Lock Block; no macro on hardware/logos; typography in post |

Reference images beat prompt tokens: with strong refs the video prompt is 30–80 words of pure camera/action/audio. See
[reference/learnings.md](reference/learnings.md) for the failure modes (LTX particle triggers, Seedance photoreal
threshold, Nano Banana geometry drift) and fixes.

## Prompting Cheat Sheet

- **Images (GPT Image 2):** `[Subject + adjectives] + [Action] + [Location] + [Composition/Camera] + [Light] + [STYLE_LOCK]` — full sentences, brief an art director. Quote any on-image text (*the label reads "NORRA"*). Name what each `--ref` is for. See [reference/gpt-image.md](reference/gpt-image.md).
- **Gemini Omni:** *"In a single continuous shot, [camera rig + move]. [What changes, with timing: 'after 3 seconds ...']. [Light]. Audio: [what you want] — no music / no dialogue if unwanted."* Refs as `<IMAGE_REF_n>`. Edits: short + *"Keep everything else the same."* See [reference/omni.md](reference/omni.md).
- **In-model effects vs. post:** ask a video model for *diegetic* effects only (smoke, light, particles, physical transformations). Text, logos, numbers and UI always go through HyperFrames (see Intake).
- **LTX 2.3 / 2.5:** one flowing present-tense paragraph; i2v = describe the *change*, not the subject; never mention particles/dust/fluids unless wanted; "Camera holds." for static.
- **FLUX 3:** brief a colleague in prose — it rewrites the prompt and fills every layer you leave unnamed. Name camera + subject/action + light + motion quality + **each audio layer** (speech in quotes with a *visible* speaker, ambience, effects, music or "no music") and end with *"no on-screen text, no subtitles"*. i2v opens *"Use this image as the first frame."* + what to leave alone. Camera: lead with the term, **one framing + one movement term** per shot, nouns from [reference/flux3-camera.md](reference/flux3-camera.md) (*Dutch angle*, *rack focus*, *Lazy Susan*, *probe lens*, *speed ramp*). Multi-shot: `SHOT ONE: … HARD CUT. SHOT TWO: …`, ~5 s per shot, adjacent shots must contrast; name the transition (*match cut*, *whip transition*, *foreground wipe*, *object portal*) when the cut should be motivated. Continuation opens *"Continue the reference video from its final frames."* Draft first. See [reference/flux3.md](reference/flux3.md).
- **Seedance 2.5 / 2.0:** `[Style preamble] + [Lock blocks] + [Scene] + time-coded beats (0-3s / 3-6s ...) + [Light/mood] + [Transition hint]`; name every reference's role (`@Image1` = product, `@Video1` = camera move). For 30 s one-shots write 6–8 time-coded beats incl. the end card. See `/seedance-prompt`.
- **Lock blocks** go into EVERY prompt for that character/set/product, verbatim.
- **One job per reference** (Seedance): "@Image 1 defines the product geometry only. Ignore the background." Conflicts resolve identity → prop → wardrobe → location → light → camera.
- **Say the sound** (LTX/Omni/Veo): anything you leave out gets invented; attach every sound to something in frame; "no music" when you score in post.
- Worked, sourced examples for each of these: [reference/examples.md](reference/examples.md).

## Error Recovery

| Problem | Fix |
|---------|-----|
| Model not found | `python scripts/list_models.py` — names change; LTX `ltx-2-*` ids retired Aug 2026; Omni = `gemini-omni-1.1-flash`; GPT Image = `gpt-image-2` |
| Omni: `no video in response` / HTTP 4xx | check the prompt for policy triggers; editing/extending uploaded video is unavailable in EEA/CH/UK; recover a finished output with `--download <interaction_id>` |
| Omni `--upscale` → "Exactly one input video is required for edit task" | uploaded-video edits are blocked in EEA/CH/UK; the script now refines the original interaction from `<clip>.mp4.json` (`--previous`) — keep sidecars next to clips |
| HyperFrames `gsap_exit_missing_hard_kill` | a fade ends within ~0.1 s of the next clip's `data-start` — move it earlier or add a `tl.set` |
| Overlay element sits in the wrong place after a templating pass | an unevaluated `{FH …}` in a plain string → invalid CSS → class position wins; `grep -o 'top:{F[HW]' index.html` |
| Highlight rings / cursor off the UI element | never guess: `measure_ui.py` and map css → frame |
| Omni clip too short / long | there is no duration field — `--duration N` writes it into the prompt; chain `--extend` for > 10 s |
| GPT Image 2 rate limit (5 img/min tier 1) | generate ≤4 stills in parallel; use `--quality medium` for coverage |
| Seedance `InputImageSensitiveContentDetected` | photoreal face → use Omni/LTX, or Seedream 5 text-only still → Seedance ([reference/seedance.md](reference/seedance.md)) |
| `media_host: no hosting configured` / S3 upload failed | set `S3_BUCKET` + `S3_REGION` in `~/config.env`, run `python scripts/media_host.py check`; without `S3_PUBLIC_URL` the script hands Ark a 24 h presigned URL (bucket can stay private) |
| Seedance `InvalidParameter.TaskTypeConstraint/Mismatch` | edit/extend/first-frame need `ratio=adaptive` (script forces), edit needs `duration=-1` and edit/remove/replace words in the prompt |
| Character / set drift | same `--ref` images every time + lock blocks; extract a clean frame from the first good clip as the new character ref |
| Props appear/disappear | put all props in the Set Lock Block from scene 1 |
| Video jitter / freeze at end of a scene | CFR convert; slot longer than source → shorten `--clip` seconds or LTX `extend` |
| `hyperframes lint` errors | read the message — usually a `<video>` inside a timed wrapper, a missing audio `id`, or `crossorigin`; see [reference/hyperframes.md](reference/hyperframes.md) |
| `check` contrast failure on overlay text | keep the text-shadow, add a scrim, or move the overlay off bright footage |
| Music shorter than film | regenerate with `--duration ≥ film length`; the builder clamps and warns |
| Subtitles out of sync | re-run whisper on the **final** vo file; check `--vo-offset` matches |
| ElevenLabs music TOS error | remove artist/brand names |
| Gemini video analysis fails on URL | non-YouTube URLs are downloaded with yt-dlp — install it (`pip install yt-dlp`); private videos can't be analyzed |
| `hyperframes init` re-links skills into `~/.claude/skills` | expected once; scaffold script sets `HYPERFRAMES_SKIP_SKILLS=1` |
| FLUX 3 `Request Moderated` / `Content Moderated` | prompt or output tripped moderation at `safety_tolerance` 2; rephrase (no real people, no brands on bodies) — raising `--safety` is for non-brand work only; a moderated output still bills |
| FLUX 3 renders the dialogue as on-screen text instead of speech | no visible speaker or missing guardrail — describe the speaker in frame, quote the exact line, add "no on-screen text, no subtitles"; off-screen lines need "off-screen voiceover says …" |
| FLUX 3 `422` on keyframes / duration | 3+ images or any `[seconds, image]` pair need an explicit `--duration`; whole seconds 5–20 (v2v 5–15); keyframe times unique and ≤ duration; v2v source ≤ 15 s and ≤ 50 MB |
| FLUX 3 clip is 1280×704 / 1920×1088, not 720p/1080p | expected (multiples of 32); `master.sh conform` / the CFR step scales it to the timeline; mono 44.1 kHz audio at model-chosen levels → loudnorm in the master |
| FLUX 3 result URL expired / `--enhance` fails | URLs live ≈ 2 h; the script downloads the mp4 and the draft `.bin` immediately — keep `<clip>.mp4.json` + `.draft_cache.bin` next to the clip; recover a finished task with `--download <id>` |

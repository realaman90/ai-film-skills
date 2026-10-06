# AI Film Studio

End-to-end AI film production for Claude Code. The agent handles creative decisions (story, prompts, pacing); pre-built scripts handle the API plumbing across image, video, audio, and final assembly.

## What it does

| Stage | Tool | Backed by |
|---|---|---|
| **Inspiration / reference analysis** | `analyze_reference.py` | Gemini video understanding (`gemini-3.8-flash`), ffmpeg scene detection, yt-dlp |
| Storyboard stills | `generate_image_gpt.py` (+ `generate_image_byteplus.py`, `generate_image_gemini.py`) | **GPT Image 2.5 Sunburst** (OpenAI, default; Flare and GPT Image 2 via `--model`); Seedream 5 (Ark) and Nano Banana 2.1 (Gemini) as fallbacks |
| Cinematic video | `generate_video_omni.py`, `generate_video_flux.py`, `generate_video_seedance.py`, `generate_video_ltx.py` (+ `generate_video_veo.py`) | **Gemini Omni 1.1 Flash**, **FLUX 3 Video** (BFL), Seedance 2.5 / 2.0 / mini, LTX 2.5 / 2.3; Veo 3.1 fallback |
| Voiceover / music / SFX | `generate_tts.py`, `generate_music.py`, `generate_sfx.py` | ElevenLabs |
| **Songs with lyrics** (lyric videos) | `generate_song.py` + `song_lyrics.py` (take scoring, line timings) | ElevenLabs Music v2.5 composition plans; local Whisper |
| **Motion design for a concept** (no footage) | `three_global.sh`, `fetch_fonts.py`, `hf_add_sfx.mjs` + [`reference/motion-design-concept.md`](reference/motion-design-concept.md) | three.js scenes in HyperFrames (`/music-to-video`, `/faceless-explainer`) |
| Asset hosting | `media_host.py` auto-uploads local refs | Amazon S3 (presigned or public URL); only needed for Seedance / Seedream |
| Assembly (fast) | `assemble.py` | ffmpeg |
| **Assembly (graphics, transitions, captions)** | `new_hyperframes_project.sh` + `build_hyperframes_timeline.py` + `render_hyperframes.sh` | [HyperFrames](https://github.com/heygen-com/hyperframes) (HTML → MP4; replaced Remotion, which lives in `legacy/`) |

Works for short films, ads, product promos and social reels. Character consistency, first/last-frame interpolation, clip extension, audio-to-video, retakes, reference-video-driven generation (Seedance 2.5) and prompt guides for each model are documented in [`SKILL.md`](SKILL.md) and [`reference/`](reference/).

## Install

With the open-source [`skills`](https://github.com/vercel-labs/skills) CLI (works for Claude Code, OpenCode, Codex, Cursor, and 50+ other agents):

```bash
npx skills add realaman90/skills          # interactive
npx skills add realaman90/skills -g -y    # global, non-interactive
```

Or clone straight into Claude Code's skills directory:

```bash
git clone https://github.com/realaman90/skills.git ~/.claude/skills/ai-film-studio
```

Either way, install the Python deps:

```bash
pip install -r requirements.txt
brew install ffmpeg          # macOS
node --version               # 22+ (HyperFrames renders via npx, pinned to hyperframes@0.8.27)
```

Trigger words: *film, movie, video, storyboard, animate, scene, voiceover, narration, soundtrack, clip, short film*.

## Setup

```bash
cp config.env.example config.env
# fill in your keys, then:
source config.env
```

Required keys (free tiers exist for most):

| Key | Provider | Used by |
|---|---|---|
| `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com/api-keys) | GPT Image stills (default 2.5 Sunburst; `GPT_IMAGE_MODEL` overrides) |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) | Omni video, reference-video analysis, Nano Banana / Veo fallbacks |
| `ELEVENLABS_KEY`, `ELEVENLABS_VOICE` | [ElevenLabs](https://elevenlabs.io) | voice, music, SFX |
| `ARK_API_KEY` | [BytePlus Ark](https://console.byteplus.com/ark) | Seedance 2.5 / 2.0, Seedream 5 |
| `LTXV_API_KEY` | [LTX Video](https://docs.ltx.video/authentication) | LTX 2.5 / 2.3 |
| `BFL_API_KEY` | [Black Forest Labs](https://dashboard.bfl.ai) | FLUX 3 Video (t2v, keyframes, continuation, draft → enhance, upscale) — files go inline as base64, no S3 |
| `S3_BUCKET`, `S3_REGION`, `AWS_*` | Amazon S3 | hosts local images/videos as URLs for Seedance / Seedream (`S3_PUBLIC_URL` optional; presigned URLs otherwise) |

## Quick start

```bash
# 0. Learn from a reference first (brief.md = style lock, pacing, shot plan, model per shot)
python scripts/analyze_reference.py --input "https://www.youtube.com/watch?v=..." \
  --goal "30s vertical product promo for X" --brand X --output refs/analysis

# 1. Storyboard still (GPT Image 2.5 Sunburst, the default)
python scripts/generate_image_gpt.py \
  --prompt "A narrow Kyoto street at dusk, lanterns lit, light rain" \
  --output scene_01.png --aspect 16:9

# 2. Animate it (Gemini Omni)
python scripts/generate_video_omni.py \
  --prompt "In a single continuous shot, slow dolly forward. Ambient evening sounds, no music." \
  --image scene_01.png --duration 6 --output clip_01.mp4

# 3. Voiceover
python scripts/generate_tts.py --text "The street remembers." --output vo.mp3

# 4. Score
python scripts/generate_music.py --prompt "Cinematic ambient strings, slow build" \
  --duration 30 --output score.mp3

# 5. Assemble
python scripts/assemble.py --videos-dir clips/ \
  --narration vo.mp3 --music score.mp3 --output film.mp4
```

For title cards, text overlays, crossfades, captions, logo bugs and end cards, assemble with HyperFrames instead:

```bash
scripts/new_hyperframes_project.sh /tmp/film --aspect 9:16
python scripts/build_hyperframes_timeline.py --project /tmp/film --clip assets/clips/a.mp4:3 \
  --end-card "brand.com|3:cta=Shop now" --music assets/audio/score.mp3 --voiceover assets/audio/vo.mp3
scripts/render_hyperframes.sh /tmp/film renders/film.mp4
```
See [`SKILL.md`](SKILL.md#step-6-assemble-with-hyperframes) and [`reference/hyperframes.md`](reference/hyperframes.md).

## Reference docs

| Topic | File |
|---|---|
| GPT Image 2 / 2.5 stills (models, migration A/B, prompting) | [`reference/gpt-image.md`](reference/gpt-image.md) |
| Gemini Omni video | [`reference/omni.md`](reference/omni.md) |
| FLUX 3 Video (modes, keyframes, multi-shot, dialogue, draft workflow) | [`reference/flux3.md`](reference/flux3.md) |
| FLUX 3 camera & style vocabulary (BFL cheat sheet: shot sizes, angles, moves, focus, lenses, time, light, transitions, rigs, VFX, art direction) | [`reference/flux3-camera.md`](reference/flux3-camera.md) |
| Camera angles for every model (five dials; 19 cards with the story job, what to write, the model's wrong cousin and its tell) | [`reference/camera-angles.md`](reference/camera-angles.md) |
| Nano Banana prompting (fallback) | [`reference/nano-banana.md`](reference/nano-banana.md) |
| Veo 3.1 prompting (fallback) | [`reference/veo.md`](reference/veo.md) |
| Seedance 2.5 / 2.0 (incl. content policy gotchas) | [`reference/seedance.md`](reference/seedance.md) |
| Seedream 5 (BytePlus stills that pass the Seedance face filter) | [`reference/seedream.md`](reference/seedream.md) |
| LTX 2.5 / 2.3 (every endpoint) | [`reference/ltx.md`](reference/ltx.md) |
| ElevenLabs voice / music / SFX | [`reference/elevenlabs.md`](reference/elevenlabs.md) |
| Inspiration / reference analysis | [`reference/inspiration.md`](reference/inspiration.md) |
| **Motion design for a concept** (pitch the concept without a reference, song or narrator, three.js scene contract, mount traps, QA) | [`reference/motion-design-concept.md`](reference/motion-design-concept.md) |
| HyperFrames assembly | [`reference/hyperframes.md`](reference/hyperframes.md) |
| Hard-learned lessons | [`reference/learnings.md`](reference/learnings.md) |

## Notes

- **Seedance blocks photorealistic human faces.** Use 3D/Pixar-style characters, product shots, or fall back to Veo / LTX. See [`reference/seedance.md`](reference/seedance.md).
- **Models change frequently.** If a script reports "model not found", run `python scripts/list_models.py` to discover current names.
- **Costs are real.** Video is paid per second — draft with Omni `--resolution 360p`, FLUX 3 `--draft` (then `--enhance` the keeper — same seed), Seedance `--model fast`/`mini` or `ltx-2-3-fast`, then upscale/regenerate the keepers. Reference analysis costs cents; run it before spending on clips.
- **HyperFrames installs its own agent skills** (`/hyperframes`, `/hyperframes-core`, …) into `~/.claude/skills` the first time it scaffolds — use them for anything beyond the generator.

## License

MIT — see [`LICENSE`](LICENSE).

### Added in 2.1.0 (2026-09-05)
`pick_takes.py` (Gemini scores takes per slot) · `jury.py` (blind quality gate) · `vo_words.py` (phrase times from VO timestamps) ·
`measure_ui.py` (headless-Chrome element boxes for overlays) · `master.sh` (conform / join / render+loudnorm / probe) ·
`cost_report.py` (spend estimate from disk) · Omni `--upscale` now refines the original interaction (works from the EEA).
SKILL.md gained: native product sections, word-synced editing, archival footage recipe, honest jury use, finals + 9:16 from one build.

### Added in 2.2.0 (2026-09-06)
`generate_video_flux.py` — FLUX 3 Video (Black Forest Labs): text / image / timed-keyframe / continuation modes, native dialogue + lip-sync,
`SHOT N / HARD CUT` multi-shot in one generation, `--draft` → `--enhance` (⅓-cost drafts re-rendered at full quality from the cached bundle),
`--upscale`, `--download` recovery, `--dry-run`; `reference/flux3.md` (API facts from the OpenAPI spec + the full prompting doctrine);
`cost_report.py` prices FLUX sidecars; `analyze_reference.py` can recommend `flux3` per shot.

### Added in 2.3.0 (2026-09-11)
GPT Image 2.5 (released 2026-09-08): `generate_image_gpt.py --model flare|sunburst` (`gpt-image-2.5-flare` / `-sunburst`),
`--quality xhigh|max`, automatic fallback to `gpt-image-2` when the key's project has no 2.5 access (`--no-fallback` to fail),
tokens + estimated $ printed per call, `GPT_IMAGE_MODEL` default override; **default still model = `gpt-image-2.5-sunburst`**
(after a 4-case A/B against GPT Image 2 and Flare). New `compare_image_models.py` runs OpenAI's
migration A/B (same prompt/refs/size/quality across models → `compare.html` + `results.json`). `reference/gpt-image.md`
rewritten for 2.5; `reference/nano-banana.md` repaired (a bulk banner insert had corrupted headings and code comments).
Fixes from an adversarial audit: `--aspect 16:9 --size 1K` is now a true 16:9 (1536×864; the old 1536×1024 is `--aspect 3:2`),
4:3 / 3:4 4K presets now fit the 8.29 MP limit, a `--mask` no longer leaks into the reference images, and cost bookkeeping
can never trigger a second (billed) generation.

### Added in 2.4.0 (2026-09-27)
**Motion design for a concept**: explain an idea, mechanism or decision as a motion video, **with or without a reference
video** (with none, the agent pitches five tellings and picks the look by eye). New `reference/motion-design-concept.md`
covers the method, the three.js scene contract for parallel builders, the mount traps and the QA bar.

New scripts:
- `generate_song.py`: ElevenLabs Music v2.5 composition plan with lyrics, returning word timestamps;
- `song_lyrics.py`: `score` picks the take Whisper understands best; `lines` gives sung line timings;
- `three_global.sh`: three.js as a classic-script global for HyperFrames;
- `fetch_fonts.py`: local woff2 + `@font-face`;
- `hf_add_sfx.mjs`: idempotent SFX cues + head scripts into `index.html`.

`elevenlabs.md` gains *Songs with lyrics*, `hyperframes.md` gains the three.js + sub-composition traps, and
`learnings.md` gains a dated entry.

### Server (shared Linux box) notes
- Keys never live in the skill folder. Ship `config.env.example`; on a server make `~/config.env` a **loader** that sources
  env files materialised from a vault (AWS SSM SecureString → `/srv/projects/.secrets/*.env` via a sync service). Split the
  film keys into their own parameter (`/<org>/film/env`: `ELEVENLABS_KEY`, `ELEVENLABS_VOICE`, `ARK_API_KEY`, `LTXV_API_KEY`, `BFL_API_KEY`,
  `S3_BUCKET`, `S3_REGION`, `S3_PREFIX`, `S3_PUBLIC_URL`) so it can be rotated without touching the shared OpenAI/Gemini keys.
- Deps: Node 22, ffmpeg, `pip install --user --break-system-packages -r requirements.txt`, then `npx hyperframes@0.8.27 --version`
  once (it downloads its own Chrome, ~114 MB). Rendering falls back to a software GPU (llvmpipe): a 2.5 s draft took 8 s on
  4 vCPU, so draft first and render finals in the background.
- Work inside the client's workspace so per-client isolation hooks apply; keep `renders/` out of any sync that pushes drafts.

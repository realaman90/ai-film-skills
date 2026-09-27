# HyperFrames — Final Assembly (replaces Remotion)

[HyperFrames](https://github.com/heygen-com/hyperframes) (HeyGen, Apache-2.0) turns **plain HTML + CSS + GSAP** into a
deterministic MP4: headless Chrome seeks every frame, FFmpeg encodes. No React, no build step, no bundler. A composition
is one `index.html` you can open in a browser, hand-edit, lint, and render.

Why it replaced Remotion here: the agent writes/reads HTML natively, `lint`/`check` catch broken timelines before a
render, media is auto-proxied, and the official agent skills (`/hyperframes`, `/hyperframes-core`, `/hyperframes-animation`,
`/hyperframes-audio`, `/media-use`, ...) are installed globally in `~/.claude/skills/` for anything beyond what the
generator below does. The old Remotion template lives in `legacy/` (and `/remotion-to-hyperframes` can port it).

Pinned CLI: `hyperframes@0.8.27` (override with `HYPERFRAMES_VERSION=`). Needs Node 22+ and ffmpeg.

---

## The fast path (what the scripts do)

```bash
# 1. Scaffold (runs `hyperframes init --example blank`, creates assets/ and renders/)
scripts/new_hyperframes_project.sh /tmp/my-film/film --aspect 9:16

# 2. Copy media in (paths inside the composition are relative to the project dir)
cp clips/cfr/*.mp4 /tmp/my-film/film/assets/clips/
cp audio/*.mp3     /tmp/my-film/film/assets/audio/
cp logo.png hero.png /tmp/my-film/film/assets/images/

# 3. Generate index.html (+ scenes.json you can re-edit and re-run with --spec)
python3 scripts/build_hyperframes_timeline.py --project /tmp/my-film/film \
    --title "NORRA|1.5:sub=Skin, simplified" \
    --clip "assets/clips/scene_01.mp4:3:text=Made for mornings" \
    --clip assets/clips/scene_02.mp4:2.5:trim=1.0 \
    --clip assets/clips/scene_03.mp4:3:audio=1 \
    --image assets/images/hero.png:3 \
    --end-card "norra.se|3:cta=Shop the serum" \
    --music assets/audio/bgmusic.mp3 --music-volume 0.15 \
    --voiceover assets/audio/vo.mp3 --vo-offset 0.8 --subtitles assets/audio/vo_subs.json \
    --logo assets/images/logo.png --logo-position bottom-right \
    --transition crossfade --transition-duration 0.5 --aspect 9:16 --fps 24

# 4. Validate (lint + runtime + layout + motion + contrast in one browser session)
(cd /tmp/my-film/film && npx --yes hyperframes@0.8.27 check)

# 5. Visual QA without a full render (PNG per timestamp; add GEMINI_API_KEY for auto-descriptions)
scripts/snapshot_hyperframes.sh /tmp/my-film/film 0.5,4,9.5,14

# 6. Render (lint first; --strict fails on lint errors)
scripts/render_hyperframes.sh /tmp/my-film/film renders/film.mp4               # high quality
scripts/render_hyperframes.sh /tmp/my-film/film renders/draft.mp4 --quality draft
scripts/render_hyperframes.sh /tmp/my-film/film renders/film.gif --format gif --fps 15
scripts/render_hyperframes.sh /tmp/my-film/film renders/film_4k.mp4 --resolution portrait-4k
```

Optional live preview (Studio, agent-safe background server):
```bash
(cd /tmp/my-film/film && npx --yes hyperframes@0.8.27 preview --background)   # then --status / --stop
```

### `build_hyperframes_timeline.py` scene syntax

| Flag | Syntax | Notes |
|------|--------|-------|
| `--clip` | `path:seconds[:trim=S][:rate=R][:text=Overlay][:audio=1]` | `trim` = skip first S seconds of the source (`data-media-start`). `rate` = playback rate, **baked into a sidecar** `x.rateR.mp4` with ffmpeg (setpts/atempo) because HyperFrames' frame extractor trips its coverage gate on `data-playback-rate`. `audio=1` extracts the clip's own soundtrack to `x.audio.m4a` (an `<audio>` must point at a real audio file) and mixes it at 0.6. |
| `--image` | `path:seconds[:text=Overlay][:kenburns=0]` | Ken Burns 1.0→1.08 scale on by default. |
| `--title` | `"Text\|seconds[:sub=Subtitle]"` | Full-frame title card, spring-in text. |
| `--end-card` | `"Text\|seconds[:cta=Call to action][:sub=..]"` | Same card with a pill CTA — use for ads. |
| `--sfx` | `path:start_seconds[:volume]` | Repeatable. |
| `--transition` | `cut \| crossfade \| blur \| dip` | Applied between every scene; `--transition-duration` (default 0.5s) is the overlap. |
| `--subtitles` | JSON `[{start,end,text}]` **or** Whisper JSON (`segments`) **or** word list | Times are relative to the voiceover; the script offsets them by `--vo-offset`. |
| `--order` | `title,clips,images,end` | Reorder scene groups. For arbitrary interleaving, edit `scenes.json` and re-run with `--spec`. |
| `--aspect` | `16:9 \| 9:16 \| 1:1 \| 21:9` | Or `--width/--height`. Fonts scale with the frame. |
| `--fade-in/--fade-out` | seconds | Black fade overlays (defaults 0.6 / 1.0). Music fades in 1.5s / out 2.5s. |

`scenes.json` (written next to `index.html`) is the editable source of truth. Reorder scenes, tweak durations, add
`"text"`, change `"transition"`, then `--spec scenes.json`.

Whisper → subtitles: `whisper vo.mp3 --model base --output_format json --word_timestamps True` then pass the `.json`.
Or `npx hyperframes transcribe` (uses whisper too). **Always transcribe the actual final VO file** — timestamps drift
between takes.

---

## The composition contract (when you hand-edit or write from scratch)

Read `/hyperframes-core` for the full rules. The ones that bite:

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="12" data-width="1080" data-height="1920" data-fps="24">
  <video id="shot-a" class="clip" data-start="0" data-duration="3" src="assets/clips/a.mp4" muted playsinline></video>
  <video id="shot-b" class="clip" data-start="shot-a - 0.5" data-duration="3.5" src="assets/clips/b.mp4" muted playsinline style="z-index:11"></video>
  <div id="card" class="clip" data-start="6" data-duration="3"><h1 id="card-h1">Title</h1></div>
  <audio id="music" data-start="0" data-duration="12" src="assets/audio/bgm.mp3"></audio>
  <audio id="vo" data-start="0.8" data-volume="1" src="assets/audio/vo.mp3"></audio>
</div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#shot-b", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.inOut" }, 2.5); // crossfade in
  tl.fromTo("#card-h1", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.7, ease: "power3.out" }, 6.1);
  tl.fromTo("#music", { volume: 0 }, { volume: 0.15, duration: 1.5 }, 0);  // absolute gain, replaces data-volume
  tl.to("#music", { volume: 0, duration: 2.5 }, 9.5);
  window.__timelines["main"] = tl;   // exactly one paused timeline per composition id
</script>
```

- **Units are seconds.** `data-start` / `data-duration` / `data-media-start` (offset into the source).
- **Relative timing:** `data-start="shot-a"` = when shot-a ends; `"shot-a - 0.5"` = overlap (spaces required!). A typo'd id silently resolves to 0.
- **Video must be `muted playsinline`; audio is always a separate `<audio id=...>`** (id is mandatory or the render is silent).
- **Never nest a `<video data-start>` inside another timed element** — lint error `video_nested_in_timed_element`. Text overlays on a clip are *sibling* clips with the same window.
- **Layering is CSS `z-index`**, not `data-track-index` (that is only a Studio lane).
- **Animation:** `gsap.fromTo()` for entrances (never `from()` against CSS `opacity:0`). No `display`/`visibility` tweens, no `repeat:-1`, no `Math.random()`/`Date.now()`, no `setTimeout`. Transform via `x/y/scale/rotation`, never `width/top/left`.
- **Transitions = incoming scene animates over the overlap**; the outgoing scene stays put underneath (exit animations are banned except on the final scene). Catalog of 40+ transitions: `~/.claude/skills/hyperframes-animation/transitions/`.
- **Volume tweens are absolute** and replace `data-volume` — carry the level in the tween (lint warns otherwise).
- **Ducking music under VO:** `data-fx-carve` on the music element, see `/hyperframes-audio`.
- Fonts: just name a Google font in `font-family`; the compiler embeds it.

Sub-compositions (`<template>` + `data-composition-src`) are how multi-scene pieces scale past ~6 scenes; the generator
keeps everything in one file on purpose (simpler to read/edit for a ≤60s film). Use `/general-video` if you outgrow it.

---

## Render flags worth knowing

| Flag | Effect |
|------|--------|
| `--quality draft\|standard\|high` | draft for iteration, high for delivery |
| `--fps 24` | overrides root `data-fps` (24 for film, 30 for social, 25 EU broadcast) |
| `--resolution portrait-4k` | renders the same composition at 2× DPR (aspect must match) |
| `--format gif --fps 15` | social loop |
| `--format mov` / `webm` | with alpha (transparent overlays for editors) |
| `--strict` | fail on lint errors (render_hyperframes.sh sets this) |
| `--variables '{"title":"Q4"}'` / `--batch rows.json` | templated variants (declare `data-composition-variables`) |

Render speed on Apple Silicon: ~1.5× realtime at 1080p draft with 5 workers. Every worker is a Chrome (~256 MB).

---

## Gotchas learned building the generator

- `hyperframes init` **also installs its agent skills into `~/.claude/skills` and `~/.agents/skills`** ("Linked skills into N agent directories"). The scaffold script sets `HYPERFRAMES_SKIP_SKILLS=1` so re-scaffolds don't touch them. Refresh deliberately with `npx hyperframes skills update`.
- Non-interactive `init` needs `--example blank` (or `--video/--audio`); otherwise it errors.
- A `.clip` element's own `right/bottom` offsets are not honored (the runtime/scaffold pins clips to `inset: 0`) — a corner logo ended up top-right. Keep clips full-frame and position the `<img>` *inside* the clip.
- An `<audio data-duration>` longer than the file → runtime warning `clip_media_fit`; the generator probes with ffprobe and clamps.
- A video slot longer than its source → HyperFrames holds the last frame (visible freeze). The generator warns; trim the slot or extend the clip with LTX.
- `data-playback-rate` on a `<video>` makes the render abort with `captured 48 of expected 60 frames (coverage 80%)` — the extractor pulls `slot × rate` seconds of source but expects `slot` frames. Bake speed changes into the file (`setpts=PTS/rate`), which is what `rate=` now does.
- An `<audio src="clip.mp4">` fails the render's asset check (`do not match their authored media element type`) even though the core docs allow it — extract the audio to `.m4a` first.
- Ken Burns scale on an `<img>` inside an `overflow:hidden` clip triggers `container_overflow` info notes → `data-layout-allow-overflow` on the img.
- Seedance/Omni/LTX outputs can be VFR. HyperFrames pre-extracts frames via ffmpeg so it copes, but convert to CFR anyway for predictable `trim`: `ffmpeg -i in.mp4 -r 24 -vsync cfr -c:v libx264 -crf 18 out.mp4`.
- `check` reports WCAG contrast on overlay text; white text over bright footage fails — add the text-shadow the generator uses or a scrim.


## Native product beats, measured plates, multi-aspect (added 2026-09-05)

- **Inject, don't screenshot.** Add a `title` scene with text `" "` to the spec, then have your overlay script replace its
  inner HTML (regex on `<div id="scene-NN" class="clip title-card">…</div>`), strip the builder's `#scene-NN-h1` tween,
  and append your CSS before `</style>` and your tweens before `window.__timelines["main"] = tl;`. All positions come
  from `FW/FH` constants so the same script builds 16:9 and 9:16.
- **Camera wrapper**: `#cam { position:absolute; width:FW; height:FH; transform-origin:0 0 }` around a wider world;
  `tl.to("#cam", { x: FW/2 − wx·s, y: FH/2 − wy·s, scale: s })` centres a world point. Mark oversized children
  `data-layout-allow-overflow`, stacked cards `data-layout-allow-overlap`.
- **Counters**: tween a plain object and write `textContent` in `onUpdate` (seek-safe); `tabular-nums` on the number.
- **Chart draw**: `stroke-dasharray` ≥ path length, tween `strokeDashoffset` to 0; fade the area fill after.
- **Plates**: if a screenshot must appear, `measure_ui.py` the element boxes; in portrait place the plate as a card
  (`object-fit: fill`, explicit left/top/width) and remap `cx/cy` for that scene.
- **Era module in portrait**: resize the `<video>` to the module rect and mask with `clip-path: inset(0 round 18px)`
  instead of a full-frame inset (builder CSS `video.clip` is cover-fit; override with the same specificity `video.era-mod`).
- **Turn-key vertical**: `ASPECT=9:16 OUT_DIR=../film_916 python3 make_spec.py && build … --project ../film_916 && ASPECT=9:16 OUT_DIR=../film_916 python3 overlays.py`;
  the vertical project dir only needs an `assets` symlink.

## three.js scenes + sub-composition mount traps (added 2026-09-27)

Full write-up in [`motion-design-concept.md`](motion-design-concept.md) §5.

- **Load three.js as a classic global** (`scripts/three_global.sh`). Put it in index.html `<head>` via `hf_add_sfx.mjs --head-js`,
  and also inside each scene's `<template>`, because lint checks each file (`missing_three_script`). Modules and
  importmaps load async, so they can lose the race with a synchronous timeline build.
- **Drive the scene from the paused timeline with a getter/setter clock,** and render as a pure function of time. The
  runtime seeks with events suppressed, so `onUpdate` alone leaves stale canvases. Use one renderer and one canvas per scene.
- **At mount, the inner root loses `data-composition-id` (it moves to the host) and its id** (it becomes
  `data-hf-authored-id`). So style and query the root as `[data-composition-id="X"]`, never `#stage[data-composition-id="X"]`.
  Otherwise the scene renders black (the script finds no root) or in Times (the root font rule never matches).
- **Never `visibility: visible`** inside a scene. It shows through the runtime's hidden host, and in the parallel render
  a late scene's layer then sits over the whole video, even when snapshots look fine. Use `inherit` / GSAP `autoAlpha`.
- **Fonts:** `fetch_fonts.py` gives local woff2 + `@font-face`. Declare it per scene; lint only auto-resolves a few families.
- **`data-layout-allow-overlap`** counts only on the overlapping text element itself, never an ancestor.


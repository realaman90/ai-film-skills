# Motion design for a concept — from an idea to a finished motion video

Use this when the job is to **explain an idea, a mechanism or a decision** as a motion video: a product architecture, a
pipeline, a policy, an ADR, a pitch. There is no footage to shoot and no product to capture. Everything is designed
motion: 3D (three.js), kinetic type, diagrams, carried by a song or a narrator.

**A reference video is optional.** Most of the time the user brings only the idea. Then **you** propose the concept, as
§1 describes. When a reference exists, it tells you the format and the look (§1b). Either way, the story comes before the
look (§2), sound comes before picture (§3), and every frame is built to be seek-safe (§5).

The examples below use one illustrative concept throughout: how a spam filter decides.

---

## 0. The shape of a run

```
idea ─► concept (pitch 5, pick 1) ─► spine (beats + facts) ─► sound (song or VO, SFX) ─► beat map
     ─► storyboard board (review) ─► scenes (one builder each, parallel) ─► assemble + patch
     ─► check + snapshots ─► render ─► look at the RENDER ─► fix ─► master
```

HyperFrames workflows to lean on (install on demand with `npx hyperframes skills update <name>`):
- **song-led** (a lyric video, or anything paced by music): `/music-to-video`. It provides the beat analyzer, frame skeleton,
  frame-worker brief and assembler.
- **narration-led**: `/faceless-explainer`.
- **short and unnarrated** (< ~15 s, one idea): `/motion-graphics`.

Read `/hyperframes` first. Its intent layer writes `BRIEF.md`; that is the only routing artifact.

## 1. The concept — you pitch it (no reference needed)

A request like "make a video explaining X" is **formed about the facts and unformed about the telling**. Five tellings
of the same facts are five different videos. So pitch before asking anything else.

1. **Write the message in one sentence**, e.g. "Every email gets a score; only the sure ones move." If you can't,
   the video isn't ready.
2. **List the mechanism's 3–6 steps.** These become the scenes.
3. **Pitch five concepts along different paths, and present all five before recommending one.**

   | Path | Example (how a spam filter decides) | Rides on |
   |---|---|---|
   | The subject's own world | the mail room as a 3D sorting machine: belts, chutes, a scanner arch | three.js machinery, camera moves |
   | The emotion | noise → calm: a screaming inbox that goes quiet one message at a time | subtractive kinetic type, audio that loses layers |
   | The audience's expectation, broken | a customs officer stamping each message INBOX / REVIEW / SPAM | tactile props, stamp hits on the beat |
   | The anti-pattern, inverted | no diagram at all: one camera move inside the filter's own score readout | a single continuous 3D move, HUD numbers |
   | An unusual format | a song whose lyrics explain it (a lyric music video) | a generated song with vocals, cuts on the beat |

   - At least **two pitches must be ones a generic model would rarely produce**. Boxes-and-arrows pipelines, cylinders
     for databases, icon grids and a talking narrator are the anti-pattern for technical explainers.
   - **Silhouette check:** sketch each pitch's major shapes. Two pitches with the same silhouette are one pitch; replace one.
4. **Recommend one, with a reason.** Mixing is a first-class answer, e.g. "A's machine with C's stamps". If the user
   says "you decide", take the recommendation and name the direction you left behind.
5. **Choose the voice.** It is part of the concept, not a later setting:

   | Voice | Pick when | Cost of the choice |
   |---|---|---|
   | **Song** (lyric video) | the audience should *remember* it; energy matters; team or social | lyrics are less exact than prose, so labels must carry the numbers |
   | **Narrator** | precision matters more than energy; a sequence of claims | slower; needs a music bed plus ducking |
   | **Silent kinetic** | ≤ 15 s, one idea, loops | no room for a mechanism with more than about 3 steps |

6. **Choose the look without a reference.** Pick 2–3 HyperFrames frame presets that fit the subject's mood
   (`/hyperframes-creative` → `frame-presets/`). Open each one's `frame-showcase.html` so the user picks **by eye**, never
   from a list of names. Technical and declarative subjects suit `broadside` (ink black and fire orange, Barlow 900 with
   IBM Plex Mono). Copy the chosen `FRAME.md` in **unmodified**; the brand is its fonts and colours. If no preset fits,
   write a `STYLE_LOCK` by hand: medium, palette (4–6 hex), type pair, line and texture, light.

### 1b. When the user *does* bring a reference

```bash
python scripts/analyze_reference.py --input ref.mp4 --goal "<length, aspect, what it explains>" --brand <Brand> --output refs/analysis
```

- **Take its format first, then its look.** A reference that looks like a HUD explainer may really be a *music video with
  sung lyrics*. When the user points at it as "the concept", they want that format, not a new concept dressed in its
  colours. Read `reference.md`'s audio lines (music, vocal, VO) before you pitch.
- **Build a contact sheet yourself** to see it: `ffmpeg -i ref.mp4 -vf "fps=16/<dur>,scale=480:-2,tile=4x4" -frames:v 1 sheet.png`.
- **Treat the analysis's numbers as fiction.** Reference analysis tends to invent product metrics (latency, accuracy,
  "zero errors"). Delete every claim the source facts don't make.
- **Honour the do-not-copy list.** Take no lyrics, melody, title, memes or third-party names from the reference.

## 2. The spine — story before look

Map the steps onto beats, and give every beat **one visual metaphor and one dominant system**:

| Beat | Job | Example (spam filter) |
|---|---|---|
| Hook | a question the viewer wants answered | one envelope drops into a slot, and a cursor waits |
| The wide state | the problem, shown | the inbox floods; a real message hides among a hundred lookalikes |
| The mechanism (hero) | the idea itself, on the strongest musical moment | each message splits into signals (sender, links, words); each gets a score; stamps land |
| The consequence | what it changes, including the failure path | spam drops into a vault; a real email caught by mistake is rescued from review |
| The order / next | what happens first, what comes last | a ladder: rules first, user reports next, retraining last |
| The end | a cold stop or CTA, held in silence | a calm, empty inbox with one unread message |

Rules:
- **Words carry the story; labels carry the facts.** Lyrics and VO tell it in plain words. On-screen HUD labels hold the
  exact numbers ("top 20 results", "p < 0.1", "500 ms").
- **Show only numbers the source facts contain.** Mark illustrative values (per-item probabilities, sample rows) as such
  in the plan, and keep every band or category represented.
- **Show the failure path.** A mechanism video that only shows the happy path reads as marketing. One beat of "and if it
  breaks, this happens" earns trust.
- **Plant everything the ending needs.** If the end names "the model", the stream has to be heading there earlier.

## 3. Sound first — the music is the spine

### Song (lyric video)

1. **Lyrics as the script.** Verses do setup, the chorus is the mechanism (the hook repeats), a spoken bridge carries a
   list or an order, and the final chorus ends on a hard stop. Aim for about one sung line per bar and 4–6 lines per section.
2. **Write the composition plan:** one chunk per section, with `duration_ms = bars × 4 × 60000 / BPM` (1,905 ms per bar at
   126 BPM). Lyrics go in `text`. Cues go in braces: `{instrumental intro}`, `{spoken, deadpan}`,
   `{ends abruptly on the last word}`. The first chunk's styles set the song's tone; give no artist names. See
   [`elevenlabs.md`](elevenlabs.md) § Songs with lyrics.
3. **Make two takes with different seeds, and pick one by clarity:**
   ```bash
   python scripts/generate_song.py --plan audio/song_plan.json --out audio/song_take1 --seed 11
   python scripts/generate_song.py --plan audio/song_plan.json --out audio/song_take2 --seed 42
   python scripts/song_lyrics.py score --plan audio/song_plan.json audio/song_take1.mp3 audio/song_take2.mp3
   ```
   Keep the clearer take, then listen to it once before building on it.
4. **Add the cold stop in the file.** Append silence so the analyzer and the timeline both see it:
   `ffmpeg -i take.mp3 -af apad=pad_dur=2.5 assets/bgm.mp3`.
5. **Get the lyric line timings** from ElevenLabs' own word timestamps:
   `python scripts/song_lyrics.py lines --plan … --take audio/song_take1 --out audio/lyric_lines.json`.

### Narrator

Use `generate_tts.py --timestamps`, `vo_words.py` anchors and a bed from `generate_music.py`. Duck the bed under the voice
(`/hyperframes-audio`).

### SFX

Use 4–6 sounds that **belong to the metaphor**: relay clicks for decisions, a stamp thud for verdicts, keystrokes for
typing and timers, an ignition sizzle, a low whoosh for things falling away. Generate them once with `generate_sfx.py` and
reuse each many times. Place them at the times the **scene builders report** their hits land (§6), not at the times the
plan guessed.

## 4. Structure on the beat (`/music-to-video`)

- Run `analyze-beatgrid.py` → `audiomap.json`. Frames cut at song sections, and every boundary snaps to a real beat.
- **Lyric sync beats roll purity.** Synthpop hi-hats make the analyzer tag most of the track as "rolls". When a boundary
  can't avoid one, put the cut where the lyric needs it.
- A frame over ~6 s gets 2+ groups at real anchors. A single continuous build, such as five ladder rungs on five spoken
  words, may stay one group.
- **Put lyrics into the plan per group**, as `[start, end] "exact words"`, straight from `lyric_lines.json`.
- **Review on a board:** `storyboard.html`, one 16:9 cell per group, showing the key moment with the real words in the
  real fonts. Get approval before building (`/hyperframes-creative` → `storyboard-recipe.md`).

## 5. Build — three.js scenes that render the same every time

One builder per scene, in parallel. Give each the `/music-to-video` frame-worker brief **plus this contract block**,
copied verbatim:

```text
three.js is the dominant system.
- window.THREE comes from the host index.html (assets/vendor/three.global.js, a classic script in <head>). Never import three,
  never a CDN. Guard: const THREE = window.THREE; if (!THREE) { DOM-only fallback, no throw }.
- ONE WebGLRenderer + ONE <canvas> per scene, shared by its groups (Chrome caps WebGL contexts; all scenes mount together).
  { canvas, antialias: true, alpha: true, preserveDrawingBuffer: true }, setPixelRatio(1), setSize(1920, 1080, false).
- Drive it from the paused GSAP timeline through a getter/setter clock, never onUpdate alone (the runtime seeks with events
  suppressed) and never requestAnimationFrame. render(t) is a pure function of frame-local t; falls use closed-form eases
  of (t - start), not physics steps. Seeded PRNG only; no Date.now / performance.now.
- Type is DOM, not WebGL: lyrics, HUD labels and readouts are HTML overlays (projected from 3D positions when they track
  objects), so text stays crisp and the layout checker can see it.
- Prefix every id and class with a per-scene tag (s1_, s2_, …): all scenes share one page.
- Style the scene root as [data-composition-id="<id>"], never #stage[...] (see the traps below).
- Never set visibility: visible (CSS or el.style) — use inherit / GSAP autoAlpha.
- Numbers on screen: exactly the ones in your block's copy. Report back the times your hits land, for SFX placement.
```

Setup the builders rely on:
```bash
scripts/three_global.sh <project>                                  # assets/vendor/three.global.js
python scripts/fetch_fonts.py --out <project>/assets/fonts "Barlow:400,600,700,800,900" "IBM Plex Mono:500"
```

### The traps that cost a render

| Symptom | Cause | Fix |
|---|---|---|
| A scene is **black** in the assembled video but fine alone | at mount, the runtime moves `data-composition-id` from the inner root to the host and renames the root id, so `document.querySelector('#stage[data-composition-id="X"]')` returns null and the script exits silently | find the root with `[data-composition-id="X"]` |
| A scene's text renders in **Times** | same cause: the root rule `#stage[data-composition-id="X"] { font-family … }` never matches | style the root as `[data-composition-id="X"]`; the runtime maps it to the inner root |
| One scene's layer shows **on top of the whole render** (snapshots looked fine) | `visibility: visible` on a child shows through the runtime's hidden host | `visibility: inherit` / GSAP `autoAlpha` |
| lint `missing_three_script` / `font_family_without_font_face` | lint checks each file and can't see the host `<head>` | add `<script src="assets/vendor/three.global.js">` and the `@font-face` block inside each scene's `<template>` |
| `content_overlap` on intentional layering (a callout over a grid, a stamp over a form) | the waiver counts only on the text element itself | set `data-layout-allow-overlap` on each overlapping text element, including ones created in JS |
| Outlined text flagged `text_not_painted` | `color: transparent` + stroke | give the fill the background colour (`-webkit-text-fill-color: <card colour>`) |
| First letter of a lyric clipped | the clip-path mask's left inset is 0 and the glyph overhangs | inset the left edge by −4 % |
| Canvas stale on some seeks | `onUpdate` alone; the runtime seeks with events suppressed | render from a clock setter as well |

## 6. Assemble, check, look, render

```bash
node <music-to-video>/scripts/assemble-index.mjs --storyboard STORYBOARD.md --hyperframes . --audiomap audiomap.json
node scripts/hf_add_sfx.mjs --index index.html --cues audio/sfx_cues.json \
     --head-css assets/fonts/fonts.css --head-js assets/vendor/three.global.js       # re-run after every assemble
npx hyperframes check . --snapshots                                                   # must pass: 0 errors
npx hyperframes snapshot . --at <every scene start and key beat> --describe false -o snapshots/review
npx hyperframes render . -q draft -o renders/video.mp4 --fps 30
ffmpeg -i renders/video.mp4 -vf "fps=16/<dur>,scale=480:-2,tile=4x4" -frames:v 1 renders/sheet.png   # look at the RENDER
scripts/master.sh render . renders/final.mp4                                          # finals: full quality, -14 LUFS
```

- **Look at the render, not only at the snapshots.** A leak from a late scene can appear only in the parallel render.
- `check` warnings you can accept: file size, "multiple instances of Three.js" (you load it in the head *and* per scene),
  and deliberate glitch overlaps that last a few frames.
- Check the audio: `ffmpeg -i video.mp4 -af volumedetect -f null -` (mean about −16 dB for a song master). The cold stop
  should read near-silent.

## 7. Quality bar — check before you call it done

- [ ] The message fits one sentence, and the video says it in the chorus or hero beat.
- [ ] Every mechanism step has its own visual metaphor, one dominant system per scene.
- [ ] Every number on screen is in the source facts; illustrative values are marked in the plan.
- [ ] Lyrics or VO are readable on screen. Each line comes in on its sung word and is out by its end; the hook is the largest type.
- [ ] Hits (stamps, rungs, locks) land on beats or sung words, and each has a sound.
- [ ] The failure path is shown.
- [ ] The end holds in silence or on a CTA; the last frame is intentional.
- [ ] `hyperframes check` passes with 0 errors, and the render's frame sheet has no leaks, black scenes or fallback fonts.
- [ ] The palette is from one preset. Changing it is one edit (the frame palette), so offer it before the final master.

## 8. Typical cost and time (an ~80 s lyric video with six scenes)

| Item | Amount |
|---|---|
| Gemini reference analysis (if there is a reference) | cents per video |
| ElevenLabs song | 2 takes × ~80 s (Music v2.5, about $0.64/min list) |
| ElevenLabs SFX | 4–6 sounds, each reused many times |
| Scene builders | 6 in parallel, about 20–30 min each |
| Check + snapshots | about 1 min per pass |
| Render (M-series, hardware GPU) | about 1–2 min for ~2,500 frames |

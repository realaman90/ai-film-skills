# FLUX 3 Video (Black Forest Labs) — text / keyframes / continuation, native audio (added 2026-09-06)

One multimodal model (announced 2026-07-23, video GA on the BFL API 2026-08-04) that generates **video + synchronized
audio** — dialogue with lip-sync in 13+ languages, ambience, effects, music — from a prompt, from 1–10 pinned images, or
by continuing a clip. 5–20 s per generation, 24 fps, `hd` (720p class) native, `fhd` (1920×1088 at 16:9) via its upsampler.
It is the one model here that will put **several shots with hard cuts inside one generation** and keep them coherent.

Script: `scripts/generate_video_flux.py` — talks REST directly (`urllib`, Python 3.9 OK). Local images/videos go inline as
base64, so **no S3 / upload step**. Key: `BFL_API_KEY` in `~/config.env` (dashboard: https://dashboard.bfl.ai).

Docs: [overview](https://docs.bfl.ai/flux_3/flux3_overview) · [video API](https://docs.bfl.ai/flux_3/flux3_video) ·
[API reference](https://docs.bfl.ai/api-reference/utility/generate-a-video-with-flux-3) · [OpenAPI](https://api.bfl.ai/openapi.json) ·
prompting: [overview](https://docs.bfl.ai/guides/prompting_video_overview) · [t2v](https://docs.bfl.ai/guides/prompting_video_text_to_video) ·
[i2v](https://docs.bfl.ai/guides/prompting_video_image_to_video) · [audio](https://docs.bfl.ai/guides/prompting_video_audio) ·
[camera terms](https://docs.bfl.ai/guides/prompting_video_camera_terms) · Runware guides (same model, richer examples):
[keyframes](https://runware.ai/docs/models/bfl-flux-3-video/guides/keyframes) · [multi-shot](https://runware.ai/docs/models/bfl-flux-3-video/guides/multi-shot-sequences) ·
[audio & speech](https://runware.ai/docs/models/bfl-flux-3-video/guides/audio-and-speech) · [continuation](https://runware.ai/docs/models/bfl-flux-3-video/guides/video-continuation)

## What it can do

| Capability | Flag | Notes |
|---|---|---|
| Text-to-video (`t2v`) | `--prompt` | 5–20 s, `--duration auto` lets the model fit the content |
| Image-to-video, first frame (`i2v`) | `--image still.png` | the still is the exact opening frame; prompt = the change |
| First + last frame | `--image a.png --last-frame b.png` | morph / land on a packshot; keep both frames the same scene + camera |
| Middle keyframes, evenly spaced (up to 10) | `--image a.png --mid-image b.png --mid-image c.png --last-frame d.png --duration 12` | plain list; the API spreads the middle frames evenly; **3+ images ⇒ set `--duration`** |
| Timed keyframes (up to 10) | `--keyframe 4.5:mid.png …` (+ `--image`, `--last-frame`) | `[seconds, image]` pairs; any timed pair with `--last-frame` ⇒ set `--duration` |
| Continue a clip (`v2v`) | `--video clip.mp4` | source ≤ 15 s, ≤ 50 MB; output is 5–15 s of *new* footage from the last frames; chain ≤ 3 |
| Draft → enhance | `--draft` then `--enhance draft.mp4 --resolution fhd` | draft ≈ ⅓ cost; enhance re-renders the *same* generation (seed + inputs cached), no re-roll |
| Upscale 1.5–3× | `--upscale clip.mp4 --upscale-factor 2 --creativity 0` | `/flux-tools/video-upscale-v1`; first 20 s; source ≤ 2560×1440 |
| Aspect | `--ratio auto\|21:9\|2:1\|16:9\|4:3\|1:1\|3:4\|9:16` | `auto` reads the prompt / the stills |
| Resolution | `--resolution hd\|fhd` (720p/1080p accepted) | `fhd` = upsampler pass on the same generation |
| Audio | on by default; `--no-audio` | dialogue + lip-sync, ambience, effects, music — all from the prompt |
| Safety | `--safety 0..4` (default 2) | brand work stays at 2; sexual capped at 3, hate at 2 regardless |
| Recover a result | `--download <task_id>` | result URLs expire ≈ 2 h; the script downloads immediately and writes `<out>.json` |
| Balance | `--credits` | GET `/v1/credits` |
| Dry run | `--dry-run` | prints the request (base64 shown as sizes), no call, no cost |

Not available: reference videos for motion/camera (use Seedance 2.5 / Omni), conversational edits of existing footage (Omni),
retake of a section (LTX 2.3 pro), audio-to-video (LTX), a seed parameter, a negative-prompt field (write negatives in prose),
a voice reference / voice-ID / audio-conditioning input (the voice is cast from prose on every generation — see *Voice consistency across clips*).

## API facts (verified against the OpenAPI spec 2026-09-06)

- `POST https://api.bfl.ai/v1/flux-3-video`, header `x-key: <BFL_API_KEY>`, JSON body keyed by `mode`
  (`t2v` | `i2v` | `v2v` | `draft_enhance`; spelled-out aliases `text-to-video`, `image-continuation`, `video-continuation`, `draft-enhance` accepted).
- Response `{id, polling_url, cost}` → `GET polling_url` (= `/v1/get_result?id=…`) every ≥ 2 s. Statuses: `Pending` → `Reasoning` →
  `Generating` → **`Ready`** | `Error` | `Request Moderated` (prompt) | `Content Moderated` (output) | `Task not found`.
  `Ready` carries `result.sample` (signed MP4 URL) and, for drafts, `result.draft_cache` (download URL of the encrypted `.bin`). `cost` = settled credits.
- Shared fields: `prompt`, `aspect_ratio` (default `auto`), `duration` (int 5–20 or `"auto"`; v2v 5–15), `resolution` (`hd` default | `fhd`),
  `generate_audio` (true), `safety_tolerance` (2), `draft` (false), `version` (`latest`).
- Audio-related request fields: **`generate_audio` only** (bool, default `true`; `false` = a silent clip with no audio track). The OpenAPI was
  searched 2026-09-06 for audio / voice / speaker / language / seed / music / subtitle: nothing else exists in any video mode. Voice, language,
  music and silence are prompt prose. (Runware exposes the same switch as `settings.audio`.)
- `i2v.keyframes`: one image string · a list of image strings (first starts, last ends, rest spread evenly; **3+ need a set `duration`**) ·
  or `[[seconds, image], …]` in time order (with `duration: "auto"` the clip runs to the last pair's second, rounded up). Images = http(s) URL or base64. Max 10.
- `v2v.start_video`: http(s) URL or base64 MP4. Aspect follows the source. Output = continuation only (join with `master.sh join` / ffmpeg concat).
- `draft_enhance.draft_cache`: base64 of the downloaded `.bin` (primary) or the URL while it is still valid; `resolution` defaults to `fhd`. The bundle pins mode, prompt, seed and inputs.
- Pricing (docs.bfl.ai, per second of output): t2v / i2v **$0.17 hd · $0.29 fhd · $0.06 draft**; v2v **$0.43 hd · $0.54 fhd · $0.12 draft**;
  draft enhance ≈ the full-quality rate (fal: $0.29/s fhd). Billed as credits, 1 credit ≈ $0.01. An 8 s hd clip ≈ $1.36; a 5-shot 20 s sequence at fhd ≈ $5.80.
- Content: safety classes are screened on the prompt *and* the output; a `Content Moderated` result still costs. Photoreal faces are fine (unlike Seedance).

## Prompting FLUX 3 — the rules that matter

**It rewrites your prompt.** A harness expands the prompt before generation: it respects explicit choices and fills in what you did not
name with sensible defaults. Consequences: prose beats keyword lists ("brief a colleague on the shot"); **every layer you leave unnamed is a
decision you gave away** — camera (defaults to a gentle drift), audio (unnamed layers are inferred from the scene — dramatic scenes tend to pull in a music bed), duration (`auto`), text (may bake subtitles).
Keep the useful part under ~1,000 characters; 5–10 named beats beat 40 adjectives. Fix a miss by adding the one missing layer, not by rewriting.

**Five things every prompt names:** subject + action (concrete verbs a camera can see) · camera (move, height, lens) · scene + light + time ·
motion quality (slow / abrupt / weightless / handheld) · audio (each layer, or "no music / no dialogue / no on-screen text").
For multi-shot work the CASTLE schema: **C**ore summary (one line) · **A**udio per shot · **S**ubject (identical wording every shot) ·
**T**imeline (timecoded camera + action) · **L**ook (realism, palette anchors, grain) · **E**nvironment (setting, light, depth of field).

**Four formats** (official): short phrase (exploration, "a red fox leaping through fresh snow, telephoto") → **one-liner** (default:
"[camera] shot of [subject] [action] in [environment]. [supporting motion / look]") → labeled fields (Camera: / Subject: / DoF: / Light: /
Motion: / Style: — tweak one line at a time) → **timestep** ("0.0–3.5 s … 3.5–7 s …", 2–3 beats per 5 s, `HARD CUT.` where the angle changes).
Start short to explore, lengthen to lock. "Name the format, not just the subject": *a 1987 local news report about…*, *archival footage of…*,
*a nature documentary about…* — the format drives camera, grade and editing more than any adjective (fal's 29-prompt test).

### Camera
Name the move relative to the subject and what the frame looks like after it: "camera locked at eye level" · "pushes slowly forward from wide to
close over 6 seconds" · "pulls slowly back, revealing the room" · "pans slowly right across the shelves" · "orbits clockwise at chest height" ·
"wide handheld tracking shot alongside". Add lens character: 35 mm shallow (documentary) · 70 mm long lens (portrait compression) · 24 mm close
(subjective handheld) · anamorphic 2.35:1 with flare (feature). One move per shot; stacking camera terms muddies it.
**Vocabulary: [flux3-camera.md](flux3-camera.md)** — BFL's cheat sheet (14 categories, 119 terms) with studio phrasing, folded in 2026-09-06.
The rules it adds: lead with the term (*Dutch angle of…*, *Rack focus from … to …*); **one framing term + one movement term** per shot, at most one
lens/optic or time treatment on top (the official unreadable example stacks four); use the nouns verbatim (*dolly zoom*, *whip pan*, *Lazy Susan*,
*probe lens*, *speed ramp*, *foreground wipe*, *object portal*, *halation*, *cinemagraph*, *split diopter*); write the frame spec in prose
("10 seconds, 16:9") when the flags are `auto`, and keep prose and flags consistent when they are not.

### Image-to-video and keyframes
- Open with **"Use this image as the first frame."** (or "…as the last frame") so the still is a hard anchor, not a style reference.
- Describe the **change**, not the subject — and add **what to leave alone**: "Hold the plate, the coulis ring and the hard side light exactly as
  they are in the still; keep the camera locked off throughout." Without that, the model re-lights and drifts.
- Start + end frame: both from the **same** scene, camera and lens (make the end frame by *editing* the start frame with GPT Image 2 `--edit`);
  the model interpolates a plausible path. Motion into/out of a pinned frame can compress; expect a re-roll when a last frame must land exactly.
- Timed keyframes: `[0, a] [4.5, b] [10, c]` — evenly spaced beats, each transition achievable, same subject wording every time. Experimental on
  scenes with large subject motion; strongest on simple compositions (unwrapping, plating, seasons, day→night, colour morphs).
- Match still aspect to output aspect (a 16:9 still at 1:1 is cropped/letterboxed). Storyboard stills for FLUX 3: `--aspect 16:9` or `9:16` at 2K.

### Multi-shot in one generation
`SHOT ONE: … HARD CUT. SHOT TWO: … HARD CUT. SHOT THREE: …` — capitals, full stops. ~5 s per shot (2 shots 8–12 s, 3 shots 12–18 s, 4 shots
= the 20 s ceiling). Adjacent shots must **contrast** (scale, angle, location or light) or they blur into one; pick a scale direction, no zig-zag.
Cut on resolved motion, not mid-gesture. Name the music bed **once** (top or tail) and ambience per shot if the mix should change. Pacing: even =
calm, accelerating = urgent, held-then-cut = release. Fewer cuts land more reliably — reach for two before three. "SHOT ONE was doing X, then Y,
then Z" is one shot with three beats, not three shots. Same locked frame with light cues across cuts = time compression ("a day in four cuts").
**Named transitions:** `HARD CUT.` is the default, not the only cut — *match cut* (shape/motion carries over), *whip transition*, *foreground
wipe* (a passing object clears onto the next scene), *object portal* (dive into a cup, out into a forest), *pass-through* (one move threads
several spaces) and *jump cut* are official nouns; write the transition where the cut should be motivated ("MATCH CUT on the rotation into SHOT
TWO"). A second register exists for montage: *"quick cuts … eight snappy shots"* over one percussive bed (official demo, 10 s) — no dialogue,
music named once; not yet run by us. Full list and phrasing: [flux3-camera.md](flux3-camera.md#shot-transitions-inside-one-generation).

### Audio — four layers, each named
Verified against the official audio guide (docs.bfl.ml `prompting_video_audio`) 2026-09-06. Rules are marked **[official]** (BFL docs) or
**[third-party]** (Runware's guide for the same model — lower authority, used only where BFL is silent); **[studio]** = our own practice.

**[official]** The prompt skeleton the docs give — you do not need all four layers; a quiet room with one line needs only speech and room tone:
```
[Shot and action].
Dialogue or voiceover: [speaker and exact words].
Ambience: [place].
Effects: [visible actions].
Music: [style and role].
```

| Layer | Write | Example (official) |
|---|---|---|
| Speech | who speaks (person · register · **recording** · delivery · guardrail), the **exact words in quotes**, how they say them | *The mechanic says, "Try it now." Quiet, matter-of-fact delivery.* |
| Ambience | the sound of the place — sources in or just outside frame | *Rain against the windows, low diner chatter, refrigerator hum* |
| Effects | sounds tied to **visible actions** (object + surface + verb) | *A ceramic mug clicks against the saucer* |
| Music | style, pace, and where it sits in the mix | *A sparse piano cue under the scene, low in the mix* |

**Speech: who is talking, and where the words go**
- **[official]** Exact words in quotation marks + who delivers them. A **visible speaker** gives the model a face to lip-sync; an **off-screen** line needs
  a literal `voiceover` or `narration` cue ("An off-screen voiceover says exactly once, '…'"). A quoted line with *neither* may be treated as text that
  belongs in the frame. Close every prompt that quotes speech with **"No on-screen text, no subtitles."** — the docs' first troubleshooting fix.
- **[third-party]** Describe the visible speaker with enough detail (age, hair, clothing) to pin *whose* mouth moves; without a face the model invents
  one or falls back to a subtitle bake. Quote every audible beat, even a sigh: *She sighs and says, "well, that's that."* renders the sigh.

**Direct the speaker — five anchors, not adjectives**
- **[official]** "Professional, warm and engaging" leaves the voice to the model and returns the same polished read every time (careful diction, even
  pauses, too much energy). Give concrete anchors instead: **Person** (age range, accent — only when it matters to the character) · **Register**
  (low, mid, bright, soft, rough) · **Recording** (close and dry · across a room · phone microphone · public-address system) · **Delivery** (lightly
  amused, hesitant, practical, talking to one friend) · **Guardrail** (no announcer delivery, no sales voice, do not over-enunciate).
  Official example: *"A British man in his thirties with a warm low-mid voice, recorded close and dry. He sounds conversational and lightly amused,
  like he is letting a friend in on something. Imperfect human timing, one relaxed breath, no announcer delivery."*
- **[official]** Use only the details that change the read — long stacks of personality adjectives fight each other, and "one audible breath" can make
  that breath too prominent. Ask for a relaxed read and judge by ear.
- **[official]** Write lines people can say (read them aloud first): contractions where the character would use them · cut the setup the viewer can
  already see · no slogan at the end of every line · give the speaker a reason to say it *to someone in the scene* · **simple punctuation — too many
  pauses turn into a sing-song rhythm.** Weak: *"Today, we are excited to embark on a transformative journey…"* Strong: *A presenter checks the monitor,
  looks back to camera, and says, "That was the hard part. Now we can see if it actually works." Dry, conversational delivery.*
- **[third-party]** Descriptor vocabulary the model reads reliably — volume (whisper, hushed, calm, raised, shouted, at conversation level) · pace
  (slowly, quickly, in a rush, drawing it out) · emotion (warmly, coldly, patiently, wearily, brightly, half-laughing) · register (formal, casual,
  intimate, professional, sarcastic, deadpan) · physical state (through gritted teeth, out of breath, half-asleep, from across the room). Two or three
  combine: *"gently, but with a note of frustration underneath"*. Undirected lines land neutral, mid-pitch, mid-pace.

**Timing inside the clip**
- **[official]** Speech takes time and may not start right away. A short line in a longer clip is safer than copy that fills every second. Timing
  instructions are a *target, not a control*: *"The voiceover speaks once and aims to finish by 8 seconds. For the final two seconds, only rain against
  the window."* Last word cut off → shorten the line, raise the duration, or ask for it to finish earlier.
- **[official]** Do not force several speakers, a long script and several visual beats into one short clip — split the scene where each part needs its
  own timing.
- **[third-party]** Pin an effect to a frame by naming both together: *"a soft clink of a spoon just as the whistle peaks"*.

**Several speakers**
- **[official]** Name each speaker by a visible role or stable description (*the orange-suited astronaut … the blue-suited astronaut*), give each a line
  and a delivery, keep turns short and separate, say "no overlap and no other speech". Two speakers in a 10 s clip is documented; attribution and
  interruptions are still **review-heavy** — judge who said what by ear before relying on it.
- **[third-party]** Direct each speaker separately or both lines can come out in one voice: *He asks flatly, "any news?" She replies, warmly but tired,
  "not really. tomorrow."*

**Ambience, effects, silence, music**
- **[official]** Specific sources beat mood words: *distant traffic and rain ticking against a metal awning* > *moody ambience*. Keep sounds tied to a
  source in or just outside the frame. When speech is the focus keep other **voices** out — crowd conversation, a talking radio, a second narrator
  compete and garble the line; weather, machinery, footsteps and traffic sit under speech safely.
- **[official]** Silence: **name a source rather than asking for quiet** — *quiet room tone* may collapse into static or dead air; *rain against the
  window, no music, no dialogue* renders. Mix too busy → keep the one or two layers the scene needs.
- **[third-party]** Music is not added unless named, *but* tension or dramatic weight pulls the model toward a bed — *"absolutely no music, only
  diegetic sound"* pins it. When you want music, write a session note: instrumentation, tempo (BPM), mood, entry/exit vs the voice ("enters under her
  first line, drops to nothing when she speaks"); "music" alone gives an unfocused wash. Foley = surface + action (*boots on wet cobblestone*, *keys
  tossed onto a marble counter*, *wine glugging into a wide glass*); name the acoustic of the space (*cavernous reverb of an empty cathedral*).
- **[official]** Multi-shot: *"Character, look, and continuity hold across hard cuts, with a single audio bed carrying through."* **[third-party]** Name
  the bed **once** (top or tail) — per-shot naming restarts it at each cut; name ambience per shot only if the mix should change.
- **[third-party]** Music is similar but never bit-identical between calls → for a film, score in post (ElevenLabs) and ask FLUX 3 for diegetic
  sound only. `generate_audio: false` drops the audio track entirely (no ambience, no silence bed) — use it when you composite all sound yourself.

**Languages and accents**
- **[official]** Many languages and accents; one performance can switch languages. Write the line as **native script**, **romanised**, or a
  **plain-language instruction** naming language + meaning (the capabilities page's own example: *"melodramatic Spanish dialogue — her gasped accusation,
  the twins answering in unison"*); quote when the exact words matter; name the language beside the line. Tight lip-sync is claimed for on-camera speech.
- **[official]** One speaker switching: label each line's language, keep the intended order, say **"the same speaker continues"** / *"using the same
  warm, lightly amused voice"*, and keep segments short enough for a natural pause. Several speakers: identify each by visible role, assign language +
  line + delivery, separate the turns.
- **[official]** Treat an accent as character + situation, paired with pace, projection, emotion and addressee (*natural Hindi delivery, warm and
  relieved* · *French spoken softly over a suit radio, with quiet wonder*) — never an isolated adjective. Language, accent, order, attribution and timing
  are "directable targets rather than exact controls"; review by ear.

**Troubleshooting [official]** — line appears as text → name a visible speaker or say `voiceover`, keep the line in quotes, add "no on-screen text or
subtitles" · sounds like an ad → replace praise words with a person, recording setup and social situation; add "no announcer delivery / no sales voice"
· sing-song → simplify punctuation, remove repetitive sentence shapes, ask for a relaxed conversational rhythm · garbled words → remove competing
speech (crowd, radio, second voice) · last word cut → shorter line, longer clip, or "finishes earlier" · generic soundscape → name each source, tie
effects to visible actions · too busy → fewer layers.

**Corrected 2026-09-06** (earlier version of this section vs the official guide): (1) dialogue is *not* limited to a visible speaker — a `voiceover` /
`narration` cue is the second documented path; (2) "stack descriptors" → a few anchors; the docs warn that stacks fight each other; (3) sing-song
cadence comes from *too many pauses / repetitive sentence shapes*, not specifically from commas and exclamation marks; (4) "one speaker per short clip"
→ two named speakers with short, separate turns is documented — the rule is not to cram speakers + script + beats into one clip; (5) the general
section's "audio defaults to an underscore" had no source — unnamed layers are inferred from the scene (third-party: music off unless named, dramatic
scenes pull a bed); (6) added the missing **Recording** anchor (close/dry, across the room, phone, PA) to the speech row.

### Voice consistency across clips
**What the docs offer — and do not.** **[official]** The audio guide has a section literally titled *Keeping a voice across clips*: *"Reuse the full
voice direction when a character returns. Keep the person, register, recording setup, and delivery wording stable, then replace only the script and
scene details. This can preserve the same kind of voice, but it does not guarantee the same performer on every generation. Treat the prompt as casting
direction rather than a fixed speaker identity. Compare takes by ear before cutting them into the same sequence."* There is **no voice reference, voice
ID, audio-conditioning input or seed field** in the API (OpenAPI searched 2026-09-06: `generate_audio` is the only audio field). Every fresh
generation re-casts the voice from prose. The only things that carry a *specific* performance forward are:
1. **The same generation.** **[official]** Multi-shot `SHOT ONE … HARD CUT. SHOT TWO …` holds character, look and continuity across the cuts with one
   audio bed — a speaker who talks in SHOT ONE and SHOT THREE is cast once (our 2026-09-06 two-shot test: same woman, no identity drift). Up to 20 s /
   ~4 shots per generation.
2. **Continuation (`v2v`).** **[official]** picks up from the final frames "carrying momentum, framing, and scene logic forward"; **[third-party]** the
   source's ambient audio layers carry over and *"a source that ends with a spoken word half-formed carries the vocal cutoff into the continuation"* — so
   the model does hear the source. Voice *identity* across a continuation is not documented anywhere; treat it as likely-but-verify.
3. **Draft → enhance.** **[official]** `draft_enhance` re-renders the *same* generation (mode, prompt, seed, inputs pinned) — the one way to get an
   identical performance twice. **Never re-roll a take whose voice you liked; enhance its draft.**

**Practical recipe [studio], strongest first**
- Put a character's lines in as few generations as possible: one multi-shot generation per scene, `v2v` to extend a talking scene (end the source on
  a natural pause or breath, never mid-word; restate the VOICE block *and* the same ambience layers at the join — "silent joins between two
  audio-heavy clips read as a break" [third-party]).
- Across separate generations, paste **the identical VOICE block verbatim** — person, register, recording, delivery, guardrails — directly before the
  quoted line, and keep the visible-speaker description (face, age, hair, clothing) identical too. Change only the words and the scene.
- Anchor the voice with **measurable** terms the studio can check, not personality words: a pitch band in Hz, a pace in words/s, a named timbre,
  accent + intonation, and negative guardrails. (Hz and words/s are our extension — the docs use age range and register words — but they are what
  lets you *reject* a take objectively.)
- Generate 2–3 drafts per line, cast by ear first (the docs' rule), then by number: mean pitch (e.g. `librosa.pyin`) within ±10 % of the band and
  pace within ±0.3 words/s of the target; reject the rest before they reach the cut. Enhance only the survivors.
- Draft the whole scene at `--draft`, listen to the voices side by side, and only then enhance — drafts are cheap and enhance keeps the seed.
- When identity must be exact and the voice is off-screen, do not fight the model: generate the picture silent (`--no-audio` or "no dialogue") and lay
  one ElevenLabs voice under the whole film. On-camera lines stay in FLUX 3 (lip-sync) and go through the recipe above.

**VOICE block template** — fill every placeholder, then paste it unchanged into every clip where the character speaks:
```
[NAME]'s voice — the same voice as in every other clip of this film: a [low | mid | bright] [alto | mezzo | tenor | baritone | …]
around [Hz] Hz, [timbre: slightly husky | clean | warm | rough | breathy], [pace word] at about [words/s] words per second,
a [light | strong | no] [accent] accent with [level | falling | lightly rising] intonation, recorded [close and dry | across the room |
on a phone | over a PA], [register: deadpan and matter-of-fact | lightly amused | practical | talking to one friend],
[guardrails: no smile in the voice, no vocal fry, no announcer delivery, no sales voice, do not over-enunciate], contractions kept.
```
Working example from the current production (paste-tested across clips):
> LINNEA's voice — the same voice as in every other clip of this film: a low alto around 165 Hz, slightly husky, dry and unhurried at about 2.3
> words per second, a light Swedish accent with level intonation, deadpan and matter-of-fact, no smile in the voice, no vocal fry, no announcer
> delivery, contractions kept.

Then the line: *She looks up from the screen and says, "It runs the strategy. You run the company." No on-screen text, no subtitles.*

### Continuation (v2v)
Open with **"Continue the reference video from its final frames."** The model reads the last seconds of picture *and* audio and carries framing,
light temperature, ambience, subject state and physics forward; the prompt says only what happens next (write from the final beat, not the whole
scene) and restates lens + light to keep the seam quiet. Design sources to end on **resolved motion, camera at rest, a clean audio beat, subject
positioned for the next action** (ask for it: "the camera comes to rest on the bottle as the last frame"). Two continuations hold, three usually,
beyond five expect drift — restart the chain from the last clean clip rather than patching. Use it surgically: add a missing ending, give a beat
runway. Source ≤ 15 s / 50 MB (hard rejects) — `ffmpeg -i in.mp4 -t 15 -c copy out.mp4`. Output is the new footage only.

### Style, time and text
Name non-photoreal styles with a recognisable reference *and* the material it leaves: "Ghibli-adjacent watercolour with visible pencil linework",
"Aardman-adjacent stop-motion clay with fingerprints", "hyper-crisp vector motion design". Time is a style: hyperlapse ("one hour compresses into
8 seconds with long-exposure blur"), timelapse, "1/8 speed slow motion", split screen ("frame split cleanly down the centre, left …, right …").
FLUX 3 renders **accurate in-scene typography** (title cards, dated captions, labels) — useful for era/documentary formats, but the studio rule
stands: brand typography, prices, claims and CTAs are composited in HyperFrames, never generated.

### Draft workflow (use it)
`--draft` = the same generation at low quality for ~⅓ the price and faster; it is *the* render, not a preview. Fix every creative decision on
drafts (composition, cut points, delivery), then `--enhance draft.mp4 --resolution fhd` reproduces that exact generation at full quality.
Prompt changes need a new draft. The sidecar stores `draft_cache_file` (the `.bin`) so enhance works after the 2 h URL expiry.

### What to avoid
keyword dumps · rewriting the whole prompt when one layer missed · duration < 5 or > 20 (v2v > 15) · stills that don't match the output aspect ·
unnamed camera (drift) or unnamed audio (invented layers) · camera terms past the cap — one framing + one movement, at most one lens/optic or time treatment on top (*low aerial handheld orbit push-in*) · quoted dialogue without a visible speaker *or* a `voiceover` cue, or without "no on-screen
text, no subtitles" · re-rolling a take whose voice you liked instead of enhancing its draft · stacked personality adjectives as voice direction ·
abstract audio ("a held breath", "subsonic dread") — least supported · overfilled short clips (dialogue clips at the end) · two mid-shots in a row
across a HARD CUT · describing the still instead of the motion · mid-gesture endings on clips you plan to continue.

## Worked examples (official / documented)

- **Locked interior with layered audio (t2v, 10 s):** "An unbroken continuous 10-second shot inside a small independent bookshop on a rainy autumn
  afternoon in Amsterdam. Warm interior light from dim brass sconces, tall dark-walnut shelves with worn hardcovers, an antique brass bell above the
  door. The camera holds locked on the empty shop for a beat, then pans slowly across the front shelves and settles on a tabby cat curled on the
  returned books by the counter, one ear twitching as thunder rolls. Audio in layers: warm interior tone, the low tick of a wall clock, muffled rain
  on the front window, a soft distant thunder roll as the cat's ear twitches. No music, no on-screen text."
- **One-liner (t2v):** "A low tracking shot of a fox sprinting through wet pine undergrowth at dawn. Mist drifts between the trees as the camera
  keeps pace. Cool blue morning light, cinematic naturalism."
- **Action that implies its own sound:** "A boxer trains alone in a dim gym. Rapid footwork on the canvas, gloves striking a worn punching bag,
  fluorescent lights buzzing overhead, handheld close follow shot, gritty documentary style."
- **Format-first (fal test set, 20 s, 720p):** "a 1987 local news report about teenagers hanging out at the mall" · "archival footage of the Wright
  brothers' first flight in 1903. No sound" (honoured: −68 dB) · "archival footage of how the Golden Gate Bridge was built" (correct dated title
  cards in sequence) · "A nature documentary about shopping carts returning to the wild." · "Einstein explaining probabilities to a professor"
  (standard dialogue coverage: two-shot, over-shoulder, singles with matching eyelines, unprompted).
- **i2v packshot to life (8 s):** "Use this image as the first frame. An 8-second clip: the camera holds locked on the knife for a beat, then a chef's
  hand enters from the top of the frame, lifts it and turns the blade so the window light runs down the edge. Hold the board, the linen and the hard
  side light exactly as they are in the still. Audio: the soft scrape of steel on wood, kitchen room tone. No music, no on-screen text."
- **Dialogue with a visible speaker:** "Close-up, 70 mm, shallow focus. A mechanic in his forties wipes his hands on a rag, looks up and says, quiet
  and matter-of-fact, 'Try it now.' A beat of stillness before he speaks. Ambience: a radio far off, a socket wrench dropped on concrete. No music,
  no announcer delivery, no on-screen text, no subtitles."
- **Voiceover:** "Off-screen voiceover, British woman in her thirties, close and dry, like letting a friend in on something, says exactly once:
  'It runs the strategy. You run the company.' She finishes by 8 seconds; the last two seconds are only the office hum. No music, no on-screen text."
- **Multi-shot (three shots, 15 s):** "Core: a morning espresso in three cuts. SHOT ONE: extreme close-up, portafilter locks into the group head,
  steam hisses, warm tungsten. HARD CUT. SHOT TWO: overhead, the crema swirls into a white cup on marble, hard side light. HARD CUT. SHOT THREE:
  wide, eye level, she carries the cup to a rain-streaked window and stops. Palette warm amber and cream throughout. Music: sparse felt piano at
  70 BPM under everything, low in the mix. Ambience per shot: hiss and clunk; pour and porcelain; rain and distant traffic. No on-screen text."
- **Continuation:** "Continue the reference video from its final frames. The runner slows to a walk over the next two seconds, then stops and bends
  forward with her hands on her knees, chest heaving. Same 35 mm handheld feel and overcast light. Audio: her breathing close, gulls far off, no music."
- **Timed keyframes (docs example):** prompt "a seed grows into a tree through the seasons", `--keyframe 0:seed.png --keyframe 4.5:sapling.png --keyframe 10:tree.png --duration 10`.

## Where FLUX 3 sits vs the other video models

| | FLUX 3 Video | Omni 1.1 Flash | Seedance 2.5 | LTX 2.5 / 2.3 |
|---|---|---|---|---|
| Faces | ✅ | ✅ | ❌ (Seedream workaround) | ✅ |
| Per-generation length | 5–20 s (+5–15 s per continuation) | 3–10 s (+extend to 40 s) | 4–30 s | 6–20 s / 2–20 s |
| Multi-shot in one take | **✅ SHOT / HARD CUT** | one continuous shot | time-coded beats, cuts OK | 2–3 max, less reliable |
| Keyframes | first · first+last · up to 10 timed | first · first+last | first · last (`image2`) | first · last |
| Reference videos / edits | continuation only | 3 × ≤3 s refs, conversational edit | 10 refs, edit/extend | retake/extend (2.3 pro) |
| Dialogue + lip-sync | **✅ 13+ languages** | ✅ | `generate_audio` | ✅ |
| Cheap drafts | `--draft` $0.06/s, enhance = same seed | 360p $0.03/s, upscale = refine | `--model mini` | `ltx-2-3-fast` |
| Cost / 8 s | $1.36 hd · $2.32 fhd · $0.48 draft | $0.80 720p · $1.20 1080p | ≈ $1.2 | $0.7–1.2 / $0.25 |
| Best for | multi-shot sequences, dialogue scenes, era/documentary formats, storyboard keyframes, silent or scored-in-post plates | hero shots you fix by talking to them, draft → 4K | 30 s one-take ads, "camera like @Video1", products/3D | budget coverage, retakes, audio-to-video |

Routing rule of thumb: a scene with **talking** or **more than one angle** → FLUX 3 first; a hero shot you expect to iterate by feel → Omni;
a 30 s product one-take with a motion reference → Seedance 2.5; coverage at scale or a fix inside an existing clip → LTX.

## Verification log

2026-09-06 — audio/speech section verified against docs.bfl.ml prompting_video_audio (+ overview / t2v / i2v / camera terms); voice-consistency subsection added.

2026-09-06 — camera vocabulary folded in from docs.bfl.ml `prompting_video_camera_terms` (14 categories, 119 terms) → [flux3-camera.md](flux3-camera.md);
Camera, Multi-shot and What-to-avoid sections updated. Vocabulary only — none of the new terms has been run live yet.

**2026-09-06 — live, four generations, ≈ $4.80 (BFL_API_KEY in `~/config.env`, 5000 credits ≈ $50 on the account).**

| Run | Settings | Wall time | Billed | Result |
|---|---|---|---|---|
| t2v fox tracking shot | 5 s, 16:9, `--draft` | 49 s | 30 credits ($0.30) | 1280×704 24 fps mono AAC; coherent low tracking shot, mist, dawn grade; `draft_cache.bin` (2 KB) saved |
| i2v from Conductor still `scene_01.png` | 8 s, 16:9, hd | 132 s | 136 credits ($1.36) | framing, stage, light held exactly; subject came to a natural stop; room tone only (−47 dB mean) |
| draft_enhance of the fox draft | `--enhance --resolution fhd` | 200 s | not reported (`cost: null`) | 1920×1088, same seed → same shots/beats as the draft, more detail; `result` = `sample`, `duration`, `seed` |
| t2v two-shot with dialogue (Scandinavian office) | 10 s, 16:9, hd | 86 s | 170 credits ($1.70) | SHOT ONE MCU to lens, **HARD CUT at 7.7 s** to the wide; same woman/sweater/desk/palette; Whisper transcribes the line verbatim; no burned-in text |

What this taught us (also in `learnings.md`):
- **Raw base64 works** for `keyframes` (no `data:` prefix), a 3 MB PNG inline is fine. Result fields: `sample` (signed MP4, US or EU delivery host),
  `prompt`, `seed`, `draft_cache` (+ `draft_caches[]`) on drafts. Signed URLs expired **1 h** after completion in practice (`se=` param) — the script downloads at once.
- **hd = 1280×704, fhd = 1920×1088** (multiples of 32, not 720/1080). The CFR conform step (`master.sh conform` / `-r 24`) and HyperFrames cover it; do not assume 1080 rows.
- Status path: `Pending` → `Reasoning` (≈ 10–20 s, the harness rewriting the prompt) → `Generating` → `Ready`. hd ≈ 10–15 s per output second; enhance to fhd took longer than the draft (200 s for 5 s).
- Audio is mono 44.1 kHz. Dialogue sat at −27 dB mean / −5 dB peak; ambience-only at −47 dB mean. Normalise in the master (`loudnorm`), never trust the model's levels.
- Multi-shot follows the prompt's shot order and cuts where the beat ends (the cut came at 7.7 s of 10, not at the "5 s per shot" rule) — pin timing with a
  timestep prompt if the cut has to land on a mark. The wide shot invented the colleagues asked for, out of focus, no identity drift on the speaker.
- `draft_enhance` returned `cost: null` on submit and on the result → `cost_report.py` prices it by rate (fhd × seconds). Check the dashboard for the exact figure.
- `--dry-run` is free and offline; `--credits` is the cheapest live check of the key.

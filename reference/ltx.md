# LTX 2.3 Video Generation (direct API)

> **2026-09 update — LTX-2.5 is live** (`ltx-2-5-fast`, `ltx-2-5-pro`, released 2026-08-11). `scripts/generate_video_ltx.py --ltx-model ltx-2-5-fast`.
>
> - Endpoints: text-to-video, image-to-video, audio-to-video, `last_frame_uri`, `camera_motion`, `generate_audio:false`. **No extend / retake / reframe on 2.5** — the script falls back to `ltx-2-3-pro` for those.
> - `ltx-2-5-fast`: 720p/1080p **6–20 s** (24/25 fps) or 6–10 s at 48/50 fps; 1440p/4K 6–10 s. `ltx-2-5-pro`: 720p/1080p, 6–10 s only.
> - `"duration": null` lets the model pick the length (credits reserved for the max, refunded).
> - Pricing per second: ~$0.09 (720p) / $0.15 (1080p) / $0.19 (2K) / $0.37 (4K).
> - `ltx-2-fast` / `ltx-2-pro` were **retired 2026-08-15** and removed from the script. LTX-2.3 stays the workhorse for extend/retake and 2–20 s clips.


Lightricks LTX — fast, affordable video generation with synchronized audio. All calls go directly to `https://api.ltx.video/v1` using the LTX-issued API key.

**Requires:** `LTXV_API_KEY` in environment. No third-party SDK — the script uses `urllib` directly.

Sources: [Authentication](https://docs.ltx.video/authentication) | [API Reference](https://docs.ltx.video/api-documentation/api-reference/video-generation/image-to-video) | [Official Prompt Guide](https://ltx.io/model/model-blog/ltx-2-3-prompt-guide) | [API Prompting Docs](https://docs.ltx.video/api-documentation/prompting-guide) | [Long Shots Guide](https://ltx.studio/blog/prompting-long-shots-with-ltx-2-how-to-build-20-second-cinematic-moments)

---

## Endpoints Overview

All endpoints are POST. The video is returned **directly as binary** (`application/octet-stream`) in the 200 response — there is no task/polling protocol.

| Endpoint | LTX Path | Use Case |
|----------|----------|----------|
| [Image-to-Video](#image-to-video) | `/image-to-video` | Storyboard still to clip |
| [Text-to-Video](#text-to-video) | `/text-to-video` | Prompt-only clip |
| [Extend](#extend-video) | `/extend` | Extend existing clip forward or backward |
| [Retake](#retake-video) | `/retake` | Re-generate a section of existing video |
| [Audio-to-Video](#audio-to-video) | `/audio-to-video` | Generate video synced to audio input |
| [Upload](#uploading-local-files) | `/upload` | Two-step pre-signed upload for local assets |

### Models (`model` field)

`ltx-2-fast`, `ltx-2-pro`, `ltx-2-3-fast`, `ltx-2-3-pro`. End-frame interpolation (`last_frame_uri`) requires `ltx-2-3`. Extend/retake accept only `ltx-2-pro` or `ltx-2-3-pro`.

---

## Authentication

All requests send `Authorization: Bearer $LTXV_API_KEY`. Get a key from the LTX dashboard.

---

## Prompting Guide (Official LTX 2.3 Best Practices)

This section is distilled from the official LTX prompting guides. **Read this before writing any prompt.**

### The Golden Rule

LTX 2.3 responds best to **long, detailed prompts**. The more specific you are about subject, action, lighting, camera movement, and audio, the closer the output matches your vision.

**Bad:** "A person walking"
**Good:** "A young woman in a red coat walking briskly through a rain-soaked Tokyo street at night, neon reflections on wet pavement, handheld camera following from behind."

### Prompt Structure (6 Elements)

Write prompts as a **single flowing paragraph** in **present tense**. Include these 6 elements in order:

1. **Establish the Shot** — Use cinematography terms matching your genre
2. **Set the Scene** — Lighting, color palette, textures, atmosphere
3. **Describe the Action** — Natural sequence flowing clearly from start to finish
4. **Define Characters** — Age, hairstyle, clothing, distinguishing features. Express emotion through **physical cues, not abstract labels**
5. **Camera Movement** — Specify how and when the camera moves
6. **Audio Description** — Ambient sound, music, speech, or singing. Place dialogue in quotation marks

### What Changed in 2.3 vs Earlier Models

- **More faithful prompt adherence** — specific descriptions of facial expressions, timing, pauses, and emotional beats translate more reliably
- **Prompt length matters more** — longer prompts consistently outperform short ones. If generating 8-10s videos, the prompt must be detailed enough to fill the duration
- **Audio descriptions have more impact** — improved audio quality makes detailed audio descriptions worthwhile
- **Break dialogue into segments** — divide long sentences into shorter phrases with acting directions between them

### Duration-to-Detail Matching

| Duration | Prompt Length | Detail Level |
|----------|-------------|-------------|
| 6s | 2-4 sentences | Single action, clear camera move |
| 8-10s | 4-6 sentences | One dominant event with setup |
| 12-16s | 6-10 sentences | Mini-scene with beats |
| 18-20s | 10+ sentences | Full scene: header + blocking + dialogue + closing |

**A short prompt for a long video results in the model rushing through the action or adding unwanted pauses.**

### Official "For best results" checklist (docs.ltx.video)

From the LTX prompting guide — follow these or you'll fight the model:

1. **Single flowing paragraph.** Not bullet points, not stanzas.
2. **Present tense verbs.** "The camera holds" ✓ — "The camera will hold" ✗.
3. **Aim for 4–8 descriptive sentences** per clip. Below 4 = not enough direction. Above 8 for a 6s clip = conflicting signals.
4. **Match detail level to shot scale.** Close-ups need MORE detail; wide shots need LESS. (Counter-intuitive — we found the opposite of what you'd expect: close-up-with-big-prompt leaks into composition changes.)
5. **Describe camera movement relative to the subject**, and describe how the subject appears *after* the movement.
6. **Start simple and layer complexity gradually.** Don't front-load. Render a short simple version, then add detail on retake.

### Static-camera phrases that work

From the official frog-yoga example and our own testing:

| Phrase | Strength |
|--------|----------|
| "Camera holds for a moment." | Best — used in the official example |
| "The camera holds." | Good |
| "Static frame." | Good |
| "Lingering shot." | Medium |
| "No zoom, no dolly, no pan, no push-in." | Good — use as a reinforcer, not alone |
| "Locked static" / "Extreme macro, locked static" | **Weak — observed to trigger push-in on i2v** |

Combine: put "Camera holds for a moment." early in the prompt AND set `--camera-motion static`. Belt-and-braces.

### Trigger words that backfire on i2v

Certain words reliably activate unwanted model behaviors on i2v. Avoid unless you actually want the effect:

| Trigger phrase | What LTX actually does |
|----------------|----------------------|
| "particle of dust drifts" / "dust motes" | Full sparkle/glitter shower across the frame |
| "slowly forms" / "drop swelling" / fluid formation | Static glass bulb sitting in the wrong place (fluid physics = AI slop) |
| "Extreme macro" (in i2v with full-bottle ref) | Aggressive push-in beyond the reference frame |
| "dolly in slightly" | Model interprets as "noticeable dolly" |
| "cinematic motion" | Model adds heavy camera moves |
| "dramatic" | Fast cuts, exaggerated lighting shifts |
| "epic" / "sweeping" | Unrequested crane/orbit moves |

**When you want genuine stillness with only light/atmosphere changes**, describe the *light itself* (e.g. "the rim light breathes slightly brighter over four seconds") and stay away from particle/dust language entirely.

### Prompt Tips by Endpoint

| Endpoint | Strategy |
|----------|----------|
| **Text-to-Video** | Start with strong visual description. You're building everything from scratch — describe subject, action, environment, lighting, camera, audio. |
| **Image-to-Video** | **Do not re-describe what is already in the image.** Describe only the transition from stillness to motion: what changes, how the camera behaves, how light evolves, the audio. Over-describing the subject makes LTX re-invent the composition. See [Image-to-Video rule](#image-to-video-rule-describe-transition-not-subject) below. |
| **Audio-to-Video** | Your audio input anchors temporal structure. Use the prompt for visual interpretation. |
| **Extend Video** | Describe what happens in the extension. Add soft closing actions. |
| **Retake Video** | Describe the replacement content for the specific section. |

### Image-to-Video Rule: describe transition, not subject

The single most load-bearing rule for i2v. From the official LTX 2.3 guide:

> "Avoid describing what's already in the input image; instead, describe the transition from stillness to motion."

**If the reference shows a bottle on a plinth, do NOT write:**
> "The matte-black NORRA serum bottle stands on dark polished stone, pump cap lying beside it. Background deep blue-black, softly out of focus. Shallow depth of field. 35mm colour negative look, light grain."

That is all visible already. LTX ends up treating the prompt as a second, competing brief and re-frames/re-interprets freely (real observed outcome: tight push-in, invented lightbulb-shaped "drop" floating above the pump, composition lost).

**Instead, write only the motion:**
> "The camera holds. Over six seconds, the cold rim light along the right edge of the frame breathes very slightly brighter, peaks at four seconds, then settles. One fine particle of dust drifts slowly through the shaft of light. No other motion. Quiet room tone."

Short, terse, transition-only. The image carries the look; the prompt carries the change.

**Phrases that reliably produce static camera:** "The camera holds." · "Camera holds for a moment." · "No camera movement at all — no zoom, no dolly, no pan, no push-in." Use multiple in the same prompt if the model is pushing in against your will. The `--camera-motion static` flag adds another explicit lock.

**When you DO need to describe the subject:** only do it if the reference image is weak (wrong angle, wrong expression) OR you're doing text-to-video. For strong reference stills, prompt length should be roughly proportional to the complexity of the *motion*, not the scene.

### What Works Well

- Cinematic compositions with varied shot scales
- Emotive human moments with subtle gestures
- Atmosphere and setting (fog, mist, golden hour, rain, reflections)
- Clear camera language ("slow dolly in," "handheld tracking")
- Stylized aesthetics (comic book, cyberpunk, painterly)
- Lighting and mood control (backlighting, color palettes, rim light)
- Voice and dialogue with multiple languages
- Single dominant event per prompt

### What to Avoid

| Mistake | Why | Fix |
|---------|-----|-----|
| Internal emotional states | Model can't render "sad" directly | Use physical cues: "eyes downcast, shoulders slumped" |
| Readable text and logos | Unreliable text generation | Add text in post-production with ffmpeg/PIL |
| Complex physics / chaotic motion | Causes artifacts | Keep motion simple and natural |
| Overloaded scenes | Too many characters = loss of clarity | Stick to 1-2 characters max |
| Conflicting lighting | "Bright sunny day with dramatic shadows" | Be consistent with light sources |
| Over-constrained numbers | "Exactly 3 birds at 45 degrees" | Use natural language descriptions |
| Short prompt + long duration | Model runs out of direction | Match detail to duration |

### Dialogue Formatting

Break long sentences into short phrases with acting directions between them:

```
A middle-aged man with greying hair speaks in a sad, slow-paced voice,
"I remember after you kids came along..." He pauses and looks to the side,
then continues, "your mom..." His eyes widen momentarily. He finishes
with a cracking voice, "said something to me I never quite understood."
The camera slowly zooms into his face.
```

**Key rules:**
- Place dialogue in quotation marks
- Add physical acting cues between phrases: pauses, glances, gestures
- Specify vocal quality: "whisper", "shout", "cracking voice", "resonant gravitas"
- Mention language/accent if non-English

### Audio Description Guide

LTX 2.3 generates synchronized audio. Describe it in your prompt:

**Ambient sounds:** "coffeeshop noise," "dripping rain and wind," "forest ambience with birds singing"
**Dialogue style:** "energetic announcer," "resonant voice with gravitas," "distorted radio-style," "robotic monotone," "childlike curiosity"
**Volume/intensity:** "quiet whisper," "mutters," "shouts," "screams"

### 20-Second Long Shot Technique

For clips 16-20s, write prompts like **mini-scenes**:

```
EXT. TOWN SQUARE - MORNING

Warm light, a quiet street, faint birdsong. An older woman in a floral
dress stands near a stone fountain, her hands clasped together. She
speaks softly: "It was never the same after they left." She pauses,
looks down at the water, then begins walking slowly along the empty
cobblestone street. The camera tracks alongside her at eye level.
After a few steps she stops, turns slightly, and looks over her
shoulder toward a man on a tractor in the distance. The camera holds
on her face for a beat, then slowly pans right to reveal the full
square. Faint church bells in the distance.
```

**Structure:**
1. Scene header (place + time)
2. Tone/atmosphere description
3. Sequential blocking (subjects + camera move together)
4. Dialogue with performance cues in brackets
5. Soft closing action (camera drift, held beat, ambient sound)

**Tips:**
- Order actions by sequence — the model follows temporal order
- Start with close-ups before wider shots to preserve facial detail
- Avoid abrupt reframing; maintain smooth natural motion
- When dialogue ends early, add transitional actions (pauses, camera drifts)
- Let the camera linger on one speaker before moving to the next

### Cinematic Vocabulary Reference

**Camera Language:**
follows, tracks, pans across, circles around, tilts upward, pushes in, pulls back, overhead view, handheld movement, over-the-shoulder, wide establishing shot, static frame, slow dolly in, crane up

**Film Characteristics:**
film grain, lens flares, pixelated edges, jittery stop-motion, slow motion, time-lapse, rapid cuts, lingering shot, continuous shot, freeze-frame, fade-in/fade-out, seamless transition, motion blur, depth of field, shallow focus

**Lighting:**
flickering candles, neon glow, natural sunlight, dramatic shadows, backlighting, rim light, golden hour, blue hour, practical lighting, high-key, low-key

**Color & Atmosphere:**
vibrant, muted, monochromatic, high contrast, desaturated, fog, rain, dust, smoke, particles, haze

**Textures:**
rough stone, smooth metal, worn fabric, glossy surfaces, wet pavement, frosted glass

**Animation Styles:**
stop-motion, 2D animation, 3D animation, claymation, hand-drawn, illustrated

**Stylized Genres:**
comic book, cyberpunk, 8-bit pixel, surreal, minimalist, painterly, illustrated, noir

**Cinematic Genres:**
period drama, film noir, fantasy, epic space opera, thriller, modern romance, experimental film, arthouse, documentary

---

## Full Prompt Examples

### Example 1: News Broadcast (Long Shot, ~20s)

```
EXT. SMALL TOWN STREET - MORNING - LIVE NEWS BROADCAST.

The shot opens on a news reporter standing in front of a row of cordoned-off
cars, yellow caution tape fluttering behind him. The light is warm, early sun
reflecting off the camera lens. The faint hum of chatter and distant drilling
fills the air. The reporter, composed but visibly excited, looks directly into
the camera, microphone in hand.

Reporter (live): "Thank you, Sylvia. And yes - this is a sentence I never
thought I'd say on live television - but this morning, here in the quiet town
of New Castle, Vermont... black gold has been found!"

He gestures slightly toward the field behind him.

Reporter (grinning): "If my cameraman can pan over, you'll see what all the
excitement's about."

The camera pans right, slowly revealing a construction site surrounded by
workers in hard hats. A beat of silence - then, with a sudden roar, a geyser
of oil erupts from the ground, blasting upward in a violent plume. Workers
cheer and scramble, the black stream glistening in the morning light. The
camera shakes slightly, trying to stay focused through the chaos.

Reporter (off-screen, shouting over the noise): "There it is, folks - the
moment New Castle will never forget!"

The camera catches the sunlight gleaming off the oil mist before pulling back,
revealing the entire scene.
```

**Why it works:** Scene header sets context. Physical descriptions ground the reporter. Dialogue broken into segments with acting cues. Camera direction integrated naturally. Audio described (chatter, drilling, cheering). Clear temporal sequence.

### Example 2: Frog Yoga (Comedy, ~15s)

```
The camera opens in a calm, sunlit frog yoga studio. Warm morning light washes
over the wooden floor as incense smoke drifts lazily in the air. The senior
frog instructor sits cross-legged at the center, eyes closed, voice deep and
calm.

"We are one with the pond." All the frogs answer softly: "Ommm..."
"We are one with the mud." "Ommm..."
He smiles faintly. "We are one with the flies."

A pause. The camera pans to the side towards one frog who twitches, eyes
darting. Suddenly its tongue snaps out, catching a fly mid-air and pulling
it into its mouth.

The master exhales slowly, still serene. "But we do not chase the flies...
not during class."

The guilty frog lowers its head in shame, folding its hands back into a
meditative pose. The other frogs resume their chant: "Ommm..."

Camera holds for a moment on the embarrassed frog, eyes closed too tightly,
pretending nothing happened.
```

**Why it works:** Establishes tone immediately. Physical comedy driven by visual beats, not dialogue alone. Camera pans timed to the comedic reveal. Character emotion shown through physical cues ("eyes closed too tightly").

### Example 3: Fashion Commercial (Image-to-Video, 8s)

```
Stylish woman in a reflective trench coat walking through a rainy neon street
at night. Slow push-in camera following from behind. Wet pavement reflections,
soft fog, confident pace. She pauses and makes a subtle head turn toward the
camera. Shallow depth of field, cinematic atmosphere. The sound of rain on
pavement, distant city traffic.
```

**Why it works:** Focuses on motion (walking, head turn) since image defines the look. Single clear camera move (push-in). Atmosphere through sensory details. Audio described.

### Example 4: Product Shot (Image-to-Video, 6s)

```
Slow dolly push toward a black quilted leather handbag sitting on a marble
counter beside white peonies in a ceramic vase. Soft natural window light from
the right. Shallow depth of field, the flowers gently shift in a breeze.
Luxury product shot, clean, minimal, elegant. Soft ambient room tone.
```

**Why it works:** For i2v, describes the motion not the existing image. Single camera move. Atmospheric detail. Short prompt matches short duration.

### Example 5: Emotional Dialogue (Text-to-Video, 10s)

```
Close-up of a woman in her 30s with auburn hair pulled back, wearing a cream
knit sweater. She sits at a kitchen table, morning light from a window to her
left. Her fingers trace the rim of a coffee mug. She looks up, eyes
glistening, and speaks softly: "I just... I thought we had more time." She
exhales and looks away, her hand moving to her collarbone. The camera holds,
static, shallow depth of field. Quiet ambient kitchen sounds, the hum of a
refrigerator.
```

**Why it works:** Physical emotion cues (tracing mug, glistening eyes, hand to collarbone). Dialogue short and specific. Static camera lets the performance breathe. Audio grounded in environment.

---

## Endpoints Reference

### Image-to-Video

**POST** `https://api.ltx.video/v1/image-to-video`
**Best for:** Storyboard-to-clip.

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `image_uri` | string | — | Yes | Source image URL or `storage_uri` from `/upload` |
| `prompt` | string | — | Yes | Motion/action description |
| `model` | string | — | Yes | `ltx-2-fast`, `ltx-2-pro`, `ltx-2-3-fast`, `ltx-2-3-pro` |
| `duration` | integer | — | Yes | Seconds (model-dependent) |
| `resolution` | string | — | Yes | e.g. `1920x1080`, `1080x1920`, `3840x2160` |
| `fps` | integer | 24 | No | Model-dependent |
| `generate_audio` | boolean | true | No | Include synchronized audio |
| `last_frame_uri` | string | — | No | End-frame for interpolation (ltx-2-3 only) |
| `camera_motion` | string | — | No | `dolly_in/out/left/right`, `jib_up/down`, `static`, `focus_shift` |

```bash
python scripts/generate_video_ltx.py \
    --prompt "Camera slowly pushes in..." \
    --image scene.png --output clip.mp4

# Pro quality
python scripts/generate_video_ltx.py \
    --prompt "..." --image scene.png --output clip.mp4 --ltx-model ltx-2-3-pro

# End frame interpolation (ltx-2-3 only)
python scripts/generate_video_ltx.py \
    --prompt "Smooth morph between scenes" \
    --image start.png --end-image end.png --output transition.mp4
```

### Text-to-Video

**POST** `https://api.ltx.video/v1/text-to-video`

| Parameter | Type | Default | Required |
|-----------|------|---------|----------|
| `prompt` | string | — | Yes |
| `model` | string | — | Yes |
| `duration` | integer | — | Yes |
| `resolution` | string | — | Yes |
| `fps` | integer | 24 | No |
| `generate_audio` | boolean | true | No |
| `camera_motion` | string | — | No |

```bash
python scripts/generate_video_ltx.py \
    --prompt "A sunset over mountain peaks, time-lapse clouds" \
    --output sunset.mp4 --endpoint text-to-video
```

### Extend Video

**POST** `https://api.ltx.video/v1/extend`

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `video_uri` | string | — | Yes | Input video URL or storage_uri (16:9 or 9:16, max 4K, ≥73 frames) |
| `duration` | number | — | Yes | Extension length (2-20s) |
| `prompt` | string | — | No | What happens in the extension |
| `mode` | string | "end" | No | `start` or `end` |
| `model` | string | `ltx-2-3-pro` | No | `ltx-2-pro` or `ltx-2-3-pro` |
| `context` | number | auto | No | Seconds of input used as context (max 20s) |

Combined context + duration frames ≤ ~505 (21s @ 24fps).

```bash
python scripts/generate_video_ltx.py \
    --prompt "She continues walking and turns the corner" \
    --video clip.mp4 --output extended.mp4 \
    --endpoint extend --duration 5 --extend-mode end
```

**Output contains only the new extension** (concatenate with ffmpeg if you want original + new).

### Retake Video

**POST** `https://api.ltx.video/v1/retake`

| Parameter | Type | Default | Required |
|-----------|------|---------|----------|
| `video_uri` | string | — | Yes |
| `start_time` | number | — | Yes (seconds) |
| `duration` | number | — | Yes (min 2s) |
| `prompt` | string | — | No |
| `mode` | string | `replace_audio_and_video` | No |
| `resolution` | string | auto | No (`1920x1080` or `1080x1920`) |
| `model` | string | `ltx-2-3-pro` | No |

**Modes:** `replace_audio_and_video` | `replace_video` | `replace_audio`

```bash
# Fix a distorted face at t=3s
python scripts/generate_video_ltx.py \
    --prompt "She smiles warmly" --video clip.mp4 --output fixed.mp4 \
    --endpoint retake --start-time 3 --duration 2

# Replace only audio
python scripts/generate_video_ltx.py \
    --prompt "Gentle rain and soft piano" --video clip.mp4 --output new_audio.mp4 \
    --endpoint retake --start-time 0 --duration 5 --retake-mode replace_audio
```

### Audio-to-Video

**POST** `https://api.ltx.video/v1/audio-to-video`

| Parameter | Type | Default | Required |
|-----------|------|---------|----------|
| `audio_uri` | string | — | Yes (2-20s) |
| `image_uri` | string | — | No* |
| `prompt` | string | — | No* |
| `resolution` | string | auto or 1920x1080 | No |
| `guidance_scale` | number | 5 (text) / 9 (image) | No |
| `model` | string | `ltx-2-3-pro` | No |

*At least one of `image_uri` or `prompt` required.

```bash
# Audio + image (music video)
python scripts/generate_video_ltx.py \
    --prompt "Woman dancing in a studio" --audio music.mp3 --image dancer.png \
    --output mv.mp4 --endpoint audio-to-video

# Audio + text only (visualizer)
python scripts/generate_video_ltx.py \
    --prompt "Abstract colorful visualizer pulsing with beat" \
    --audio track.mp3 --output viz.mp4 --endpoint audio-to-video
```

Output is 25 fps. Higher `guidance_scale` = more literal prompt adherence.

### Uploading Local Files

**POST** `https://api.ltx.video/v1/upload` (empty body, just auth header).

Response:
```json
{
  "upload_url": "https://...",
  "storage_uri": "ltx://...",
  "expires_at": "2025-...",
  "required_headers": {"Content-Type": "image/png"}
}
```

Then PUT the file bytes to `upload_url` with the listed headers. Pass `storage_uri` back in subsequent endpoint calls as `image_uri`, `video_uri`, or `audio_uri`.

The script handles this automatically — just pass `--image local.png` (or `--video`, `--audio`) and it uploads on your behalf.

---

## Constraints & Gotchas

### Duration Limits

| Endpoint | Min | Max |
|----------|-----|-----|
| Image-to-Video / Text-to-Video (fast) | 6s | 20s |
| Image-to-Video / Text-to-Video (pro) | 6s | 10s |
| Extend | 2s | 20s |
| Retake | 2s | — |
| Audio-to-Video | 2s | 20s (driven by audio length) |

### Key Constraints
- Images / videos / audio must be reachable via HTTPS URL, or uploaded via `/upload` -> `storage_uri`
- Match image aspect ratio to output for best results
- Audio-to-Video: `guidance_scale` defaults differ (5 text, 9 image)
- End-frame (`last_frame_uri`) only works with ltx-2-3 family models
- **No face blocking** — unlike Seedance, LTX works with photorealistic faces

### Common Quality Killers (from ComfyUI guide)
1. Wrong aspect ratio
2. CFG/guidance scale too high
3. Overstuffed prompts with competing actions
Fix these three before tuning anything else.

---

## When to Use Which Endpoint

| Scenario | Recommended |
|----------|------------|
| Storyboard still to clip (budget) | image-to-video + `ltx-2-3-fast` |
| Storyboard still to clip (quality) | image-to-video + `ltx-2-3-pro` |
| No reference image | text-to-video |
| Transition between two frames | image-to-video + `last_frame_uri` (ltx-2-3) |
| Make a clip longer | extend |
| Fix bad section in a clip | retake |
| Replace audio only | retake + `mode=replace_audio` |
| Music video / audio sync | audio-to-video |
| Product ad synced to jingle | audio-to-video + image |
| Long cinematic moment (20s) | image-to-video or text-to-video fast + detailed prompt |

---

## Comparison with Other Models

| Feature | Veo 3.1 | Seedance 2.0 (Ark) | LTX 2.3 Fast | LTX 2.3 Pro |
|---------|---------|-------------------|-------------|-------------|
| Provider | Google | BytePlus Ark (direct) | Lightricks (direct) | Lightricks (direct) |
| Human faces | Works | BLOCKED | Works | Works |
| Max duration | 8s | ~12s | 20s | 10s |
| Max resolution | 4K | ~720p | 2160p | 2160p |
| Extend video | No | No | Yes | — |
| Retake section | No | No | Yes | — |
| Audio sync | Built-in | `generate_audio` | audio-to-video | — |
| End frame | Yes (full) | Yes (image2) | Yes | Yes |
| Best for | Quality, faces | Products, 3D, motion refs | Budget, long clips | Quality clips |

---

## Tested Examples (from Chanel bag ad project)

### Example: Bridge Walk (Image-to-Video Fast, 8s)

- **Endpoint:** image-to-video (fast)
- **Input:** `https://pub-a836d08629454caf9059acebd385a714.r2.dev/chanel-ad/scene_03_bridge.png`
- **Prompt:** "Elegant Asian woman walks across a Parisian bridge at golden hour. She wears a cream tweed jacket and blue jeans, black quilted handbag on her shoulder. Camera tracks from the side. Wind gently moves her hair. Seine river and Haussmann buildings in warm backlight. Cinematic, fashion editorial, 35mm film look."
- **Settings:** duration=8, resolution=1080p
- **Result:** `bags-ad/v2/ltx/03_bridge_walk.mp4` (4.7 MB)
- **Cost:** $0.32

### Example: Street Walk (Image-to-Video Fast, 8s)

- **Endpoint:** image-to-video (fast)
- **Input:** `https://pub-a836d08629454caf9059acebd385a714.r2.dev/chanel-ad/char_ref.jpg`
- **Prompt:** "Medium shot, stylish Asian woman in beige tweed jacket and blue jeans walks briskly along a Parisian cobblestone street past a warm-lit bookshop. She carries a black quilted handbag with gold chain on her shoulder. Camera tracks alongside her. Pedestrians blur in background. Golden hour, 35mm film grain, shallow depth of field, fashion commercial."
- **Settings:** duration=8, resolution=1080p
- **Result:** `bags-ad/v2/ltx/02_street_walk.mp4` (5.7 MB)
- **Cost:** $0.32
- **Notes:** No face blocking (Seedance rejected same image). Character preserved well from input.

### Example: Texture Close-Up (Image-to-Video Fast, 6s)

- **Endpoint:** image-to-video (fast)
- **Input:** `https://pub-a836d08629454caf9059acebd385a714.r2.dev/chanel-ad/scene_01_texture.png`
- **Prompt:** "Extreme close-up of black quilted leather surface. Light slowly drifts across revealing diamond pattern stitching and gold chain hardware. Shallow depth of field. Luxury fashion film, soft studio lighting, cinematic."
- **Settings:** duration=6, resolution=1080p
- **Result:** `bags-ad/v2/ltx/01_texture_open.mp4` (8.6 MB)
- **Cost:** $0.24

### Example: Hero Product Push (Image-to-Video Fast, 6s)

- **Endpoint:** image-to-video (fast)
- **Input:** `https://pub-a836d08629454caf9059acebd385a714.r2.dev/chanel-ad/scene_04_hero.png`
- **Prompt:** "Slow dolly push toward a black quilted leather handbag sitting on a marble counter beside white peonies in a ceramic vase. Soft natural window light from the right. Shallow depth of field, the flowers gently shift in a breeze. Luxury product shot, clean, minimal, elegant."
- **Settings:** duration=6, resolution=1080p
- **Result:** `bags-ad/v2/ltx/04_hero_push.mp4` (1.9 MB)
- **Cost:** $0.24

<!--
ADD MORE EXAMPLES HERE as you test each endpoint:

### Example: [Name] ([Endpoint], [Duration])
- **Endpoint:** [which one]
- **Input:** [image/video/audio URL or path]
- **Prompt:** "..."
- **Settings:** duration=X, resolution=Y
- **Result:** [path to output] (size)
- **Cost:** $X.XX
- **Quality notes:** [what worked, what didn't, learnings]

ENDPOINTS STILL NEEDING EXAMPLES:
- [ ] Image-to-Video Pro
- [ ] Text-to-Video Fast
- [ ] Text-to-Video Pro
- [ ] Extend Video
- [ ] Retake Video
- [ ] Audio-to-Video
-->

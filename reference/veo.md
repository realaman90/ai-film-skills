> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Veo 3.1 -- Complete Video Prompting Guide

Source: Google Cloud Blog "The ultimate prompting guide for Veo 3.1" + Google DeepMind prompt guide + Vertex AI docs

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Models

| Model | Resolution | Duration | Audio | Key Features |
|-------|-----------|----------|-------|--------------|
| `veo-3.1-generate-preview` | 720p/1080p/4K | 4-8s | Native | Extension, refs, interpolation |
| `veo-3.1-lite-generate-preview` | 720p/1080p | 5-8s | Native | Faster, cheaper, no 4K/extension |
| `veo-3-generate-preview` | 720p/1080p | 4-8s | Native | Extension, interpolation |
| `veo-2-generate-preview` | 720p | 5-8s | Silent | 1-2 per request |

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Constraints
- 1080p/4K require `duration_seconds=8`
- Extensions: 720p only, max 148s total, veo-3.1 only (not lite)
- Reference images: up to 3, veo-3.1 only (not lite)
- Frame interpolation: veo-3.1 only (not lite), duration must be 8s

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Prompt Formula (from Google's official guide)

```
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
```

- **Cinematography:** Camera work and shot composition
- **Subject:** Main character or focal point
- **Action:** What the subject is doing
- **Context:** Environment and background elements
- **Style & Ambiance:** Aesthetic, mood, and lighting

**Front-load the most important element.** The model prioritizes what comes first.

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Prompt Length
- **50-75 words:** Single-focus scenes
- **75-125 words:** Most projects (sweet spot)
- **125-175 words:** Complex scenes requiring precise control
- **Over 175 words:** Risk overloading with conflicting instructions

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Camera Movements (ONE per clip)

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Movement Types

| Movement | Prompt Language | Effect |
|----------|----------------|--------|
| Static | `static shot, fixed camera` | Stability, focus |
| Pan L/R | `slow pan from left to right` | Survey, reveal |
| Tilt up/down | `camera tilts upward from feet to face` | Reveal character |
| Dolly in | `slow dolly in on her face` | Tension, intimacy |
| Dolly out | `dolly out to reveal the landscape` | Scale, revelation |
| Dolly zoom | `dolly zoom creating vertigo effect` | Disorientation |
| Tracking | `tracking shot following him as he walks` | Follow action |
| Crane up | `crane shot ascending from ground to aerial` | Grandeur, scale |
| Crane down | `crane descending from sky to street level` | Approach, arrival |
| Orbit/Arc | `camera performs 180-degree arc around subject` | Dynamic perspective |
| Aerial/Drone | `aerial shot rising and pulling back` | Establish scale |
| Handheld | `slight handheld movement, documentary style` | Raw, authentic |
| Steadicam | `smooth steadicam through the hallway` | Fluid elegance |
| Whip pan | `fast whip pan to the right` | Energy, transition |
| Fly through | `camera moves through the space continuously` | Immersion |

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Shot Sizes

| Shot | Prompt Language | Use |
|------|----------------|-----|
| ECU | `Extreme close-up of her eye` | Detail, emotion |
| CU | `Close-up of hands holding the letter` | Intimacy |
| MCU | `Medium close-up, head and shoulders` | Conversational |
| MS | `Medium shot, waist up` | Standard narrative |
| Full | `Full shot, entire body visible` | Character context |
| WS | `Wide shot of the lighthouse` | Establish location |
| ELS | `Extreme long shot, tiny figure against vast ocean` | Scale, isolation |

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Camera Angles

| Angle | Prompt Language | Effect |
|-------|----------------|--------|
| Eye level | `Camera at eye level` | Neutral, balanced |
| Low angle | `Low angle looking up` | Power, imposing |
| High angle | `High angle looking down` | Vulnerability |
| Bird's eye | `Overhead, directly down` | Geography, pattern |
| Dutch angle | `Slight Dutch angle tilt` | Unease, tension |
| POV | `First-person POV at eye level` | Immersion |

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Lens Choices

| Lens | Effect |
|------|--------|
| `16mm wide-angle` | Expands space, exaggerates depth |
| `35mm` | Natural perspective, documentary |
| `50mm` | Human eye perspective |
| `85mm` | Background compression, flattering portraits |
| `macro lens` | Extreme detail close-ups |
| `fisheye` | Distorted spherical look |
| `shallow depth of field` | Isolate subject with blur |
| `deep focus` | Everything sharp |
| `rack focus` | Shift attention between subjects |

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Lighting -- Name a Physical Source

**Core rule:** Always name a PHYSICAL light source. This gives Veo lighting logic that stabilizes shadows.

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Never Say This / Always Say This

| Bad | Good |
|-----|------|
| "well-lit" | "lit by soft daylight from a side window" |
| "dramatic lighting" | "single hard spotlight from upper left, deep shadows" |
| "nice atmosphere" | "lit by neon signs reflecting off wet pavement" |

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Light Sources

**Natural:** Golden hour, overcast daylight, moonlight, dappled forest light, window light
**Artificial:** Neon signs, fluorescent, candlelight, screen glow, streetlights, spotlight
**Mixed:** Window light in interior, streetlights at dusk

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Cinematic Lighting Styles

| Style | Description |
|-------|-------------|
| Rembrandt | Triangle of light on far cheek |
| Film noir | High contrast, deep shadows, single source |
| High-key | Bright, minimal shadows, upbeat |
| Low-key | Predominantly shadows, moody |
| Volumetric | Visible rays through fog/dust |
| Chiaroscuro | Strong light/dark contrast |

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Audio Direction

Veo 3.1 generates synchronized audio. If left undefined, you get random sounds.

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Dialogue
Use quotation marks. Attribute to described character.

**Colon syntax prevents subtitles:** `The founder says: "This cuts setup time in half."`

**Voice characteristics:** `"says in a weary voice"`, `"whispers nervously"`, `"announced triumphantly"`

**Multi-character:** `A man in a red hat says, "Where is the rabbit?" Then the woman in the green dress replies, "There, in the woods."`

**Keep to one breath.** Clips are ~8 seconds. Long lines get rushed or cut off.

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# SFX
```
SFX: Thunder cracks in the distance
SFX: Footsteps crunching on frost, steady breaths in cold air
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Ambient
```
Ambient: The quiet hum of a starship bridge with occasional electronic beeps
Ambient: Waves crashing, distant seagulls, gentle wind
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Music
```
Slow-building thriller score with low strings and subtle pulses
Upbeat acoustic guitar with light percussion, optimistic morning energy
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Layered Example
```
Neon buzzes softly. Static crackles from unseen speakers. A low electrical hum pulses beneath the rain.
```

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Style & Aesthetic Keywords

**Visual formats:** Photorealistic, Film noir, Documentary, Cartoon, Claymation, Anime, Watercolor, Graphic novel, Art Deco, VHS aesthetic, Cyberpunk

**Film stock:** `Shot as if on 35mm film with natural grain`, `16mm documentary footage`, `Anamorphic widescreen`

**Tone:** Happy, Melancholic, Suspenseful, Peaceful, Epic, Romantic, Eerie, Gritty, Warm, Minimal

**Atmospheric:** Fog/mist, Rain, Snow, Dust particles, Heat shimmer, God rays

**Anti-AI texture keywords:** `Fine skin pores, visible fabric weave, subtle contrast, no gloss or sharpening` -- material cues like "charcoal cotton" give Veo a light-reflection profile that stabilizes subjects across motion.

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Timestamp Prompting

Direct multi-beat sequences in a single generation:

```
[00:00-00:02] Medium shot from behind explorer pushing aside jungle vine.
[00:02-00:04] Reverse shot of her freckled face, awe-struck. SFX: Leaves, bird calls.
[00:04-00:06] Tracking shot into clearing, hand on carved stone wall. Wonder.
[00:06-00:08] Wide crane shot revealing vast temple complex. SFX: Orchestral swell.
```

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Advanced Workflows

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Ingredients to Video (Character + Set Consistency)

Provide reference images of character, object, or style. The model maintains consistency across shots. Now includes audio generation.

```python
ref1 = types.VideoGenerationReferenceImage(
    image=types.Image.from_file(location="character_ref.png"), reference_type="asset"
)
ref2 = types.VideoGenerationReferenceImage(
    image=types.Image.from_file(location="location_ref.png"), reference_type="asset"
)

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(prompt="..."),
    config=types.GenerateVideosConfig(
        reference_images=[ref1, ref2],
        person_generation="allow_adult",
        duration_seconds=8,
    ),
)
```

**Multi-shot dialogue scene pattern:**
```
Shot 1: "Using the provided images for the detective, the woman, and the office setting,
create a medium shot of the detective behind his desk. He looks up at the woman
and says in a weary voice: 'Of all the offices in this town, you had to walk into mine.'"

Shot 2: "Using the provided images for the detective, the woman, and the office setting,
create a shot focusing on the woman. A slight, mysterious smile plays on her lips
as she replies: 'You were highly recommended.'"
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# First & Last Frame (Controlled Transitions)

Generate a natural video transition between two provided images, complete with audio. Use for:
- Camera arcs/rotations around a subject
- Transformations (object changes state)
- Scene transitions with controlled start/end

```python
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(
        prompt="Camera performs smooth 180-degree arc, starting front-facing and ending behind.",
        image=types.Image.from_file(location="start.png"),
    ),
    config=types.GenerateVideosConfig(
        last_frame=types.Image.from_file(location="end.png"),
        person_generation="allow_adult",
        duration_seconds=8,
    ),
)
```

**Singer example (from Google's guide):**
```
Start frame: "Medium shot of female pop star singing into vintage microphone, dark stage, single dramatic spotlight."
End frame: "POV from behind singer on stage, looking out at cheering crowd, stage lights creating lens flare."
Prompt: "The camera performs a smooth 180-degree arc shot, starting with the front-facing view
of the singer and circling around her to seamlessly end on the POV shot from behind her on stage.
The singer sings: 'when you look me in the eyes, I can see a million stars.'"
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Clip Chaining (Seamless Scene Continuity)

**This is the key technique for visual continuity across clips.** Each clip shares a connected frame with the next.

**Pattern:**
1. Generate Clip 1 from Frame A (storyboard still)
2. Extract the LAST frame of Clip 1
3. Use that last frame as the FIRST frame of Clip 2
4. Generate a new end frame for Clip 2 (or just use image-to-video)
5. Repeat for all clips

**Result:** Camera position, lighting, props, and character identity stay consistent because each clip literally starts where the previous one ended.

```bash
> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Extract last frame from a clip
ffmpeg -sseof -0.1 -i clip_01.mp4 -frames:v 1 -q:v 2 clip_01_lastframe.jpg

> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Use as first frame for next clip
python scripts/generate_video_veo.py \
    --image clip_01_lastframe.jpg \
    --prompt "Continue the motion. Camera slowly pushes in..." \
    --output clip_02.mp4
```

**Why this matters:** Without clip chaining, each clip is generated independently -- the AI reinvents the room layout, prop positions, and lighting every time. With chaining, the visual state carries forward.

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Video Extension (up to 148s)

Extend shots without breaking continuity. Keep camera angle, lighting, and subject position unchanged.

```python
extend_op = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    source=types.GenerateVideosSource(
        prompt="Extend from the final frame. Keep camera angle, lighting, and position unchanged. Continue with slow forward drift. In the final 3 seconds, let motion settle.",
        video=initial_op.result.generated_videos[0].video,
    ),
    config=types.GenerateVideosConfig(resolution="720p"),
)
```

**Extend prompt pattern:**
```
Extend the clip by [N] seconds from the final frame.
Keep camera angle, lighting, and [key props] unchanged.
Continue with [subtle motion description].
In the final [2-3] seconds, [resolution: settle, fade, hold].
```

**Constraints:** 720p only. Max total duration 148s. Full model only (not lite).

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Image-to-Video Prompting (IMPORTANT)

When using a storyboard still as the first frame, the image already defines subject, setting, composition, and style. **Do NOT redescribe what's visible in the image.**

Focus the prompt ONLY on:
- **Camera movement** -- what the camera does
- **Action** -- what changes from the still
- **Audio** -- sound direction

**Bad (over-describing):**
```
An elderly Japanese man with white hair and round spectacles sits at a wooden workbench
surrounded by clocks in a dark workshop lit by a single lamp. He slowly sets down his tools
and looks around. Pendulums begin slowing.
```

**Good (action + camera + audio only):**
```
Slow pull-back from medium to wide. Pendulums on the walls gradually slow down.
Pale blue-white light begins emanating from the clock faces. Dust motes catch the light.
Ambient: Ticking gradually slowing, low ethereal resonance building.
```

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Anti-AI Texture Techniques

Specify micro-details and material cues to prevent the "AI plastic" look:

```
Fine skin pores and visible fabric weave. Subtle contrast, no gloss or sharpening.
```

Material cues give Veo a light-reflection profile that stabilizes subjects:
- `charcoal canvas jacket` -- not just "dark jacket"
- `worn leather apron with oil stains` -- not just "apron"
- `cream linen shirt, slightly wrinkled` -- not just "white shirt"

Reference film stocks for natural texture:
- `Shot on 35mm film with natural grain`
- `16mm documentary footage aesthetic`
- `1980s color film, slightly grainy`

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Action & Physics

Use **force-based verbs** for realistic motion: push, pull, strike, slam, sway, ripple, spiral, drift, flutter.

Describe motion as choreography:
- Camera-subject relationship (camera follows, camera stays still as subject moves)
- Speed and direction (slowly drifting left, rapidly ascending)
- Secondary motion (hair flutter, rain streaks, fabric ripple, dust swirl)

**One dominant action per prompt.** Stacking simultaneous conflicting actions causes instability. If you need complex choreography, use timestamp prompting to sequence beats.

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Cinematic Editing Terms Veo Understands

| Term | What it does |
|------|-------------|
| Match cut | Cuts between two visually similar compositions |
| Jump cut | Abrupt cut forward in time |
| Establishing shot | Wide shot setting the location |
| Montage | Rapid sequence of related images |
| Split diopter | Both foreground and background in sharp focus |

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Common Mistakes

| Mistake | Fix |
|---------|-----|
| Multiple camera movements | ONE movement per clip |
| Multiple simultaneous actions | One dominant action; sequence across clips |
| Exact counts ("five people") | Descriptive: "a small group of colleagues" |
| No light source named | Always name physical source |
| Abstract language ("experiences rain") | Observable verbs: "opens umbrella as wind gusts" |
| No audio direction | Always specify or sounds get random |
| Over 175 words | Front-load, be concise |
| Internal contradictions | "sunny" + "moonlight" = broken |
| Lengthy dialogue | One breath, 1-2 sentences max |
| Negative language | Positive: "empty street" not "no cars" |
| Redescribing the input image | Only describe what CHANGES from the still |
| No material cues | Specify fabrics/surfaces for stable rendering |
| Clips don't connect | Use clip chaining (last frame → first frame) |
| Subtitle burn-in on dialogue | Use colon syntax: `says: "line"` + `(no subtitles)` |

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Prompt Length Guide

| Length | Words | Best For |
|--------|-------|----------|
| Short | 50-75 | Single-focus scenes, simple actions |
| Medium | 75-125 | Most projects (sweet spot) |
| Long | 125-175 | Complex scenes requiring precise control |
| Too long | 175+ | Risk overloading with conflicting instructions |

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Modular Prompt Format (for complex scenes)

```
Camera: [Shot type, angle, movement]
Subject: [Character or object with specific details]
Action: [What the subject is doing -- ONE dominant action]
Setting: [Location, time of day, environmental details]
Style: [Visual aesthetic, material cues, mood]
Audio: [Dialogue with colon syntax, SFX:, Ambient:, music direction]
```

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Config Parameters

```python
types.GenerateVideosConfig(
    person_generation="allow_adult",   > **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# "dont_allow" | "allow_adult" | "allow_all"
    aspect_ratio="16:9",               > **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# "16:9" | "9:16"
    number_of_videos=1,
    duration_seconds=8,                > **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# 4 | 5 | 6 | 8
    resolution="720p",                 > **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# "720p" | "1080p" | "4k"
    generate_audio=True,               > **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Vertex AI only. AI Studio always generates audio
    seed=42,                           > **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Improves consistency across regenerations
    negative_prompt="wall, frame",     > **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Describe unwanted elements as nouns/adjectives
)
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Cost Optimization
- Disable audio when adding custom soundtrack: 50% savings (Standard), 33% (Fast) -- Vertex AI only
- Start at 720p for iteration, upgrade for final
- Use veo-3.1-lite for drafts, full model for production
- Use `seed` parameter to improve consistency when regenerating

---

#> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Example Prompts (from Google's guide)

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Office Worker (all 5 elements)
```
Medium shot, a tired corporate worker, rubbing his temples in exhaustion,
in front of a bulky 1980s computer in a cluttered office late at night.
Lit by harsh fluorescent overhead lights and the green glow of the monochrome monitor.
Retro aesthetic, shot as if on 1980s color film, slightly grainy.
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Crane Shot (reveal)
```
Crane shot starting low on a lone hiker and ascending high above,
revealing they are standing on the edge of a colossal, mist-filled canyon at sunrise.
Epic fantasy style, awe-inspiring, soft morning light.
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Bus Window (mood + material cues)
```
Close-up with very shallow depth of field, a young woman's face,
looking out a bus window at the passing city lights with her reflection
faintly visible on the glass, inside a bus at night during a rainstorm.
Melancholic mood with cool blue tones, moody, cinematic.
Fine skin pores, subtle contrast, no gloss.
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Timestamp Prompting (multi-beat in single clip)
```
[00:00-00:02] Medium shot from behind explorer pushing aside jungle vine.
[00:02-00:04] Reverse shot of her freckled face, awe-struck.
    SFX: Rustling leaves, distant exotic bird calls.
[00:04-00:06] Tracking shot into clearing, hand on carved stone wall. Wonder.
[00:06-00:08] Wide crane shot revealing vast temple complex.
    SFX: Swelling, gentle orchestral score.
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Product Reveal (timestamp + pacing)
```
Create a single continuous 8-second cinematic product reveal for a premium wireless headphone.
0-3 seconds: Dark minimalist studio, headphone in soft silhouette on matte surface.
    Camera stays steady, building anticipation.
3-6 seconds: Slow side-light sweep, camera gently pushes closer,
    revealing form, texture, and material details.
6-8 seconds: Full focus clean close-up. Camera settles confidently.
    Premium finish, polished lighting.
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Video Extension
```
Extend the clip by 7 seconds from the final frame.
Keep camera angle, lighting, and headphone position unchanged.
Continue with a very slow forward drift as soft highlights move across the surface.
In the final 3 seconds, let motion settle and fade in minimal text: "Premium Sound."
End on a steady hold with no cuts or new elements.
```

##> **2026-09: Veo 3.1 is now the FALLBACK.** Default Google video model is Gemini Omni 1.1 Flash — see `omni.md` and `scripts/generate_video_omni.py`. This script is `scripts/generate_video_veo.py`.

# Film Noir Dialogue (ingredients + colon syntax)
```
Using the provided images for the detective, the woman, and the office setting,
create a medium shot of the detective behind his desk. He looks up at the woman
and says in a weary voice: "Of all the offices in this town, you had to walk into mine."
(no subtitles)
```

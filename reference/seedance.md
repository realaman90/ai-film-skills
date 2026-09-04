# Seedance 2.0 — Video Generation

> **2026-09 update — Seedance 2.5 is live on Ark** (`dreamina-seedance-2-5-260628`, released 2026-08-06). `scripts/generate_video_seedance.py --model 2.5`.
>
> | | Seedance 2.5 | 2.0 (`--model full`) | 2.0 fast | 2.0 mini (`--model mini`, `dreamina-seedance-2-0-mini-260615`) |
> |---|---|---|---|---|
> | Max duration | **4–30 s** (or `-1` auto) | 4–15 s | 4–15 s | 4–15 s |
> | Refs per request | **50** (30 img + 10 video + 10 audio, ≤30 s of A/V refs) | 15 (9+3+3) | 15 | 15 |
> | Audio-only reference | ✓ | ✗ | ✗ | ✗ |
> | Resolution | 480p / 720p / 1080p (10-bit) | up to 4K | 720p | 720p |
> | Output | mp4, **mov** (yuv444p + PCM) | mp4 | mp4 | mp4 |
> | Edit / extend a video | ✓ (`--task-type edit|extend`, source 4–30 s) | ✓ | ✓ | ✓ |
> | First/last frame roles | `--first-frame` / `--last-frame` (ratio auto→`adaptive`) | same | same | same |
>
> Rules the API enforces (the script forces them): first-frame, edit and extend tasks need `ratio=adaptive`; **edit** needs `duration=-1`; edit prompts must contain *edit / add / remove / replace*, extend prompts *extend / continue*. `--task-type reference` skips the intent guess. Reference-image roles are named in the prompt as `@Image1`, `@Video1`, `@Audio1`.
> Real faces are **still blocked** (verification/likeness authorization via the Ark console, or their 10k virtual-human library); the Seedream 5.0 workaround below still applies. Activation needs a >USD 30 balance or a 2.5 resource pack.


Direct access via **BytePlus Ark** (`dreamina-seedance-2-*` models). The helper script `scripts/generate_video_seedance.py` handles task submission, polling, and download. Local reference files are uploaded to **Amazon S3** by `scripts/media_host.py` (presigned 24 h URL unless `S3_PUBLIC_URL` is set); Cloudflare R2 is no longer the default.

Sources: [BytePlus Ark docs](https://docs.byteplus.com/en/docs/ModelArk/1520757) | [Community Skill (MIT)](https://github.com/dexhunter/seedance2-skill)

---

## API Access

| Endpoint | Method | Notes |
|----------|--------|-------|
| `https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks` | POST | Submit generation task, returns `{id}` |
| `https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{id}` | GET | Poll for `status` and result video URL |

Auth header: `Authorization: Bearer $ARK_API_KEY`.

### Models

| Model ID | CLI flag | Use case |
|----------|----------|----------|
| `dreamina-seedance-2-0-260128` | `--model full` (default) | Final renders, best quality |
| `dreamina-seedance-2-0-fast-260128` | `--model fast` | Drafts, iteration |

---

## CRITICAL: Face Blocking Policy

**Seedance blocks photorealistic human faces** in input images/videos. Error code: `InputImageSensitiveContentDetected.PrivacyInformation` (HTTP 400). Message: *"The request failed because the input image may contain real person."*

This affects photoreal faces from ANY source — real photographs, Nano Banana, Veo, Midjourney, DALL-E. The classifier is threshold-based on visual photorealism, not provenance.

**What passes:**
- 3D / Pixar-style characters
- Product-only shots (no faces)
- Texture / detail close-ups
- Abstract / stylized content
- Landscapes, architecture
- **Seedream 5.0 text-only outputs** (they sit just under the photorealism threshold)

**What gets blocked:**
- Any photorealistic human face from external image models
- Grid overlays on faces (still blocked)
- Partially obscured faces (still blocked)
- **Seedream 5.0 outputs using `--ref` image references** (they're *too* photoreal once style-locked)

**If you need a photoreal character in a Seedance beat, use the Seedream → Seedance workflow below. Otherwise Veo 3.1 or LTX 2.3 handle faces directly.**

---

## Bypassing the real-person filter via Seedream 5.0

The only repeatable path to get an AI character into a Seedance clip.

**The pipeline:**
1. Generate the character still with **Seedream 5.0** (BytePlus's own image model).
2. Upload the result to S3 (automatic).
3. Feed to Seedance as the first-frame reference.

Because Seedream outputs carry a subtle AI aesthetic that the Seedance filter tolerates, they pass where Nano Banana / Veo stills don't. BytePlus has also indicated that model-native outputs from the same account within 30 days are "trusted" as inputs (see [Digital Character Library](https://docs.byteplus.com/en/docs/ModelArk/2223965)) — the observed behavior matches that policy, though the classifier itself still decides case-by-case.

### The filter-threshold gotcha (hard-learned)

Not every Seedream output passes. Observed:

| Seedream call | Output feel | Seedance accepts? |
|---------------|-------------|-------------------|
| Text-only prompt, no `--ref` | Slightly softer AI aesthetic | ✅ Yes |
| Single `--ref` product image + detailed prompt | Too photoreal, studio-clean | ❌ Blocked |
| Multi `--ref` (character + scene + product) | Hyper-photoreal | ❌ Blocked |

**Rule:** for Seedance input, prefer text-only Seedream generation. If you must use `--ref`, stack "documentary amateur" language heavily in the prompt (see `seedream.md` → "Documentary prompt pattern") to pull the output back under the filter's photoreal threshold.

### Workflow: `generate_image_byteplus.py` → `generate_video_seedance.py`

```bash
# Step 1 — Seedream text-only, documentary aesthetic
python scripts/generate_image_byteplus.py \
    --prompt "Amateur iPhone phone-mirror selfie, young woman early 20s post-workout, white-tiled gym locker room, cool overhead fluorescent, slight green cast, natural unretouched skin, visible pores, slight fly-away hair, documentary Kinfolk aesthetic, not a fashion editorial, not beauty retouched, a matte-black pump serum bottle on the sink beside her water bottle and keys" \
    --size 1440x2560 \
    --output gen/gym_20s.jpeg

# Step 2 — feed directly to Seedance
python scripts/generate_video_seedance.py \
    --prompt "Vertical phone mirror selfie. Static camera. She exhales slowly, lowers the phone a few centimetres, her eyes flick to the bottle on the sink, the corner of her mouth softens." \
    --image gen/gym_20s.jpeg \
    --model full --duration 6 --ratio 9:16 \
    --output out/B_gym.mp4
```

### Brand-exact branding in Seedream outputs

Seedream 5.0 **garbles uncommon typography** — "Å", "Ö", "N°", Swedish compound words. For brand-accurate wordmarks:
- Let Seedream produce the scene with a generic-looking matte-black bottle.
- Composite the actual brand bottle onto the scene in Remotion / ffmpeg / After Effects at assembly time using a frame-locked still overlay.
- OR accept that in lifestyle beats the bottle reads correctly at video playback distance even without perfect typography — viewers stitch branding from your hero / typography beats.

### Alternative: Digital Character Library

BytePlus offers a [Digital Character Library](https://docs.byteplus.com/en/docs/ModelArk/2223965) of pre-vetted virtual characters that bypass the filter. Not applicable when you need specific casting, but useful for generic lifestyle scenes.

---

## System Constraints

### Input Limits

| Type | Limit | Formats | Notes |
|------|-------|---------|-------|
| Reference images | Up to 9 | JPEG, PNG, WebP | First = opening frame if referenced in prompt |
| Reference videos | Typically 1-3 | MP4 | For camera/motion/effects replication |
| Reference audio | 1 | MP3, WAV | For BGM/voice tone |

All references must be reachable via HTTPS URL. The script auto-uploads local files to Amazon S3 (`scripts/media_host.py`; `S3_BUCKET` + `S3_REGION`, presigned 24 h URL unless `S3_PUBLIC_URL` is set).

### Request Body Shape

```json
{
  "model": "dreamina-seedance-2-0-260128",
  "content": [
    {"type": "text", "text": "<prompt>"},
    {"type": "image_url", "image_url": {"url": "https://..."}, "role": "reference_image"},
    {"type": "video_url", "video_url": {"url": "https://..."}, "role": "reference_video"},
    {"type": "audio_url", "audio_url": {"url": "https://..."}, "role": "reference_audio"}
  ],
  "generate_audio": true,
  "ratio": "16:9",
  "duration": 11,
  "watermark": false
}
```

### Response Shape

**Submit:** `{ "id": "task_xxx", ... }`

**Poll GET** `/tasks/{id}`:
```json
{
  "id": "task_xxx",
  "status": "queued" | "running" | "succeeded" | "failed" | "cancelled",
  "content": { "video_url": "https://..." },
  "error": { "code": "...", "message": "..." },
  "usage": { ... }
}
```

### Output Characteristics
- Ratios: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `21:9`
- Resolution: ~720p output
- `generate_audio: true` produces synchronized audio (dialogue + SFX + BGM as described in prompt)
- **Variable Frame Rate (VFR)** — convert to CFR in post if concatenating

---

## CLI Usage

```bash
# Basic image-to-video
python scripts/generate_video_seedance.py \
    --prompt "Camera slowly dollies forward, gentle product rotation" \
    --image product.png --output clip.mp4

# Hosted URL (no upload needed)
python scripts/generate_video_seedance.py \
    --prompt "..." --image-url https://example.com/scene.png --output clip.mp4

# Multiple references (opening frame + end frame)
python scripts/generate_video_seedance.py \
    --prompt "..." --image start.png --image end.png --output clip.mp4

# Reference video (replicate camera movement) + reference audio (BGM)
python scripts/generate_video_seedance.py --prompt "..." \
    --image scene.png --ref-video ref.mp4 --ref-audio bgm.mp3 --output clip.mp4

# Fast model, portrait, longer
python scripts/generate_video_seedance.py --prompt "..." \
    --image scene.png --output clip.mp4 --model fast --ratio 9:16 --duration 11
```

## Raw curl (reference)

```bash
curl -X POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "dreamina-seedance-2-0-260128",
    "content": [
      {"type": "text", "text": "YOUR PROMPT"},
      {"type": "image_url", "image_url": {"url": "https://.../img1.jpg"}, "role": "reference_image"}
    ],
    "generate_audio": true,
    "ratio": "16:9",
    "duration": 8,
    "watermark": false
  }'

# Then poll:
curl -H "Authorization: Bearer $ARK_API_KEY" \
  https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/$TASK_ID
```

---

## The Seedance prompt structure (official higgsfield template)

Source: [higgsfield Seedance prompting guide](https://higgsfield.ai/blog/seedance-prompting-guide). This is the canonical structure Seedance 2.0 responds to best — use it as the skeleton for every clip longer than ~4 seconds.

### Required declarations at the top (opener)

Every prompt opens with a **style/camera declaration line**. For multi-shot sequences:

```
Montage, multi-shot action Hollywood movie, don't use one camera angle or single cut,
cinematic lighting, photorealistic, 35mm film quality, professional color grading,
sharp focus, high detail texture, film grain, depth of field mastery, ARRI ALEXA aesthetic
```

For single-shot locked POV:

```
Single continuous shot, first-person POV perspective, the camera IS [her/his] eyes,
hyper-chaotic handheld motion, completely unstabilized, ... wide-angle lens (strong distortion),
subtle chromatic aberration near frame edges, 15 seconds, no music only raw SFX,
cinematic lighting, photorealistic, grounded realism, strong 35mm film look, heavy film grain
```

For locked gladiator-style POV (smoother):

```
One continuous shot, POV [character] perspective in [location], no cuts, no zoom,
natural head movement
```

Adapt per shot type. The opener primes Seedance for the whole clip.

### Required declaration at the bottom (footer)

Every prompt ends with:

```
Total: 15s / 6 shots / 16:9
```

Format: `Total: <duration>s / <shot count> / <aspect ratio>`. Without this, Seedance invents its own cuts and pacing. **This is the single biggest lever on multi-shot clips.**

### Middle section — three formats

Pick one per clip based on shot structure:

**Format A — Multi-shot (`Shot 1:`, `Shot 2:`, ...)**
Best for: montages, commercials, transformation sequences, beat-driven ads.

```
[Scene-level description — characters, environment, overall arc, one paragraph]

Shot 1: [framing, subject action, camera behavior, lighting, beat length]
Shot 2: ...
Shot 3: ...
Shot 4: ...
Shot 5: ...
Shot 6: ...

Total: 15s / 6 shots / 16:9
```

**Format B — Single shot with timed segments (`0–3s:`, `3–6s:`, ...)**
Best for: POV action, continuous sequences, dance / fight choreography, hero product reveals with scripted beats.

```
Single continuous shot 15s: [opening framing].

0–3s: [beat description]
3–6s: [beat description]
6–9s: [beat description]
9–12s: [beat description]
12–15s: [beat description]

Total: 15s / 1 shot / 16:9
```

**Format C — Minimal**
Sometimes the shortest prompts hit hardest. When the reference image + one sentence nails the intent, trust it. Higgsfield's working example: `"Fight of a 3D person with 2D"`.

### Inline VFX brackets

Specify power / effects / post inline using brackets, *inside* the action description:

```
fractal lightning veins explode across both forearms [VFX: branching electric circuits
pulsing with white-blue current, sparks jumping between fingers]
```

Seedance treats bracketed content as render-time VFX direction rather than physical action. Keep the action prose readable by not over-stuffing brackets.

### The "realism override" phrase

For monsters, creatures, skin, or anything that risks looking plasticky:

```
no 3D, no cartoon, no VFX
```

Add this at the end of the style declaration line when you need grounded realism for a creature/skin surface.

### Speed ramps

Slow-motion is precise in Seedance — use explicit transitions:

```
RAMPS TO SLOW MOTION for the [specific action]
SNAPS BACK to full speed
```

Capitalization is intentional — Seedance responds to these as timing markers.

### Canonical technical vocabulary (proven to work)

Stack these in the opener declaration line when you want "expensive commercial" feel:

- `heavy film grain` · `sharp but imperfect focus` · `noticeable focus breathing`
- `motion blur on fast actions` · `halation on highlights` · `soft highlight rolloff`
- `slightly desaturated tones` · `ARRI ALEXA aesthetic` · `practical VFX feel, minimal CGI look`
- `natural imperfections` · `subtle chromatic aberration near frame edges` · `wide-angle lens (strong distortion)`

For anamorphic commercial: `anamorphic 35mm, shallow depth of field` · For dark industrial: `harsh single-source overhead industrial light casting deep dramatic shadows, warm amber tone on skin with cool steel-blue environment`.

---

## Commercial production workflow — "build characters and locations first"

Source: [higgsfield $350K commercial guide](https://higgsfield.ai/blog/ai-commercial-youtube-guide).

The single most important methodology for multi-scene ads: **do not go scene-to-scene generating images in isolation.** Instead:

1. **Lock characters first.** Generate 1-3 reference images per character using Seedream / Nano Banana. Keep the best as the "character sheet." These become your canonical `@character_name`.
2. **Lock locations next.** Generate each location (bathroom, kitchen, lobby, corridor) once, pick the best, reuse them as `@location_name`.
3. **Every scene prompt attaches BOTH** the relevant character sheet AND the relevant location reference — not one or the other.
4. Use the phrase **"inspired by reference, not copied"** when you want interpretation; use **"preserve original color grade, preserve original grain, preserve original exposure"** when you want faithful recreation.

### Reference-tag patterns (proven)

- `@Orlando` → the male spy character (consistent across 5 scenes)
- `@Maria` → the female lead (consistent)
- `@hologram_img` → a specific prop (the watch hologram)
- `<<<image_1>>>`, `<<<image_2>>>` → positional-inline placeholders inside a dialogue prompt, to direct Seedance to cut to specific attached images at specific moments

Example (from the commercial guide):
```
@Orlando with a slight smirk says: "Yes, lady. Sometimes the right place finds
you before you find it." Static camera. Shot 1: Close-up on <<<image_1>>>;
a micro-smile... Shot 2: Close-up on <<<image_2>>>
```

### Keyframe start-end pairs for transitions

For transitions between scenes / major beat changes, set:

- **Start keyframe** — "Close-up of white pedestal holding perfume bottle" (the current state)
- **End keyframe** — "Add hand with the pistol to the top right corner, make the guy turn his head and look to the pistol, remove red lasers and fill the man with red lights" (the new state the clip should resolve to)

Seedance interpolates the action between the two keyframes. This is how you chain scene-level transformations without losing coherence.

### Rule: every scene prompt must include

1. A **scene description** (1-2 sentences — what the scene is about)
2. **Character references** (attached images + `@` tags inline)
3. **Location reference** (attached image + instruction: "inspired by reference location, reconstructed" or "preserve original exposure")
4. A **shot breakdown** (Shot 1 / Shot 2 / ... OR timed 0–3s / 3–6s / ...)
5. The **total declaration** (`Total: 15s / 3 shots / 16:9`)

Missing any of these → pacing drift, composition drift, or character drift.

### Character sheet — the exact prompt that works

Source: [higgsfield AI short film guide](https://higgsfield.ai/blog/ai-short-film-youtube-guide).

**Before generating any scene**, build a canonical character sheet for each cast member. Feed the sheet as a multi-image reference to every subsequent scene.

**Target layout (7 panels, two horizontal rows):**

Top row — full-body turnaround:
- Front (full-body)
- Left profile (full-body)
- Right profile (full-body)
- Back (full-body)

Bottom row — portraits:
- Front close-up (head and shoulders)
- Left profile close-up
- Right profile close-up

**Canonical generator prompt** (run via Seedream 5.0 or Nano Banana 2 with a single starter reference of the character):

```
Create a professional character reference sheet based strictly on the uploaded
reference image. Use a clean, neutral plain background (light grey or white).
Top row: four full-body turnaround views — front, left profile, right profile,
back. Bottom row: three head-and-shoulders portrait close-ups — front, left
profile, right profile. Identical lighting across every panel (soft three-point
studio lighting, 5500K). Maintain PERFECT identity consistency across every
panel — same face shape, same hair, same skin tone, same proportions, same
wardrobe. Neutral expression throughout, no smile, no mouth open, eyes forward
in each panel except profiles. Output a crisp, ultra-realistic, print-ready
reference sheet at 2560×1440 or higher. Not a fashion editorial. No text labels.
```

**Usage:** save the sheet as `refs/character_sheets/<name>.jpeg`. Attach it as the first reference image on every scene prompt in which that character appears. Tag the character as `@Name-Role` (hyphenated, so Seedance parses it as one token).

### Location sheet — the exact prompt that works

**Target layout (7 panels, two horizontal rows):**

Top row — 4 coverage angles:
- Straight-on frontal wide
- Left-angled wide
- Right-angled wide
- Reverse wide view (looking back the other way)

Bottom row — 3 detail close-ups of key environmental elements (props, textures, lighting fixtures, windows).

**Canonical generator prompt:**

```
Create a professional location reference sheet based strictly on the uploaded
reference image. Match the exact realistic visual style and lighting of the
reference. Arrange into two horizontal rows. Top row: four coverage angles of
the same location — straight-on frontal wide, left-angled wide, right-angled
wide, reverse wide. Bottom row: three detailed close-ups of key environmental
details (props, textures, light sources, materials). Preserve the same time
of day, same lighting direction, same color palette, same weather, same mood
across every panel. Output a crisp, ultra-realistic, print-ready location
reference sheet at 2560×1440 or higher. No people, no text labels.
```

**Usage:** save as `refs/location_sheets/<scene>.jpeg`. Attach as the second reference image (after the character sheet) on every scene in that location.

### Character tag convention

- Use `@Name-Role` with a hyphen: `@Adil-Cop`, `@Dave-Cop`, `@Selena-Wife`, `@Maren-20s`, `@Ingrid-40s`
- Hyphens keep the tag atomic so Seedance doesn't split it on spaces
- Tag every character in every sentence where they speak or act: *"@Maren-30s tilts the glass carafe, pouring water..."*
- If a scene has multiple characters, tag each one on their first mention and on every subsequent action beat they do

### Dialogue embedded inline

Source format from the short film guide:

```
Interior police cruiser, daytime, DVR dashcam look. @Dave-Cop looks forward:
"Little Kazakh spot on 5th. Plastic tables. Soup so hot it files a complaint."
@Adil-Cop replies dryly: "Sounds nice!"
```

Rules:
- Dialogue in **double quotes** immediately after a colon following the character's tag
- Delivery notes before the colon: *dryly*, *excitedly*, *whispering*, *voice cracking*
- Break long lines into shorter phrases with acting cues between them
- For radio / dispatch / off-screen voice: describe the audio source (e.g. *"Close-up of a police radio clipped to the officer's vest. The radio crackles and dispatch comes through: '[message]'"*)

### Shot-length target (short film / commercial)

**5 to 7 seconds per shot** is the working range:
- Dialogue-heavy scenes → single continuous 5–7s shot with inline dialogue
- Transitions / establishing → 5s
- Action beats → 6–7s with speed ramps
- Splits: if two quick dialogue exchanges, break into 2 × 3s or 3 × 2s shots

### Environment-specific aesthetic injection

Stack one of these phrase sets on top of the canonical style opener to lock a specific feel:

**Police / procedural:**
```
DVR dashcam look, soft overexposed sunlight, cheap digital sensor, compression
artifacts, washed-out colors, wide-angle lens distortion
```

**Security / CCTV:**
```
High-angle corner CCTV lens, wide fisheye distortion, subtle scan lines, slight
chromatic noise, faint vignette, surveillance artifacts, 24fps industrial feed
```

**Home video / amateur:**
```
Consumer camcorder feel, mini-DV compression, slight VHS bleeding, 4:3 aspect
ratio framing inside 16:9 letterbox (optional), timestamp overlay (if appropriate)
```

**Polished commercial / luxury product:**
```
Anamorphic 35mm, shallow depth of field, heavy film grain, halation on
highlights, soft highlight rolloff, slightly desaturated tones, ARRI ALEXA
aesthetic, practical VFX feel, minimal CGI look
```

**News / documentary:**
```
ENG broadcast camera, shoulder-mounted handheld, natural ambient lighting,
minimal stabilization, real-location sound, news ticker visible (optional)
```

---

### Commercial pacing targets

Distilled from the higgsfield e-commerce skill + commercial guide:

| Duration | Typical shots | Section split (approx) |
|----------|---------------|------------------------|
| 6 s | 1-2 | 2s hook · 3s show · 1s end card |
| 15 s | 4-6 | 2s hook · 10s show · 3s end card |
| 30 s | 8-12 | 2s hook · 20s show (2-4 lifestyle beats) · 5s product hero · 3s end card |
| 60 s | 14-20 | 3s hook · 42s show (4-6 beats with narrative arc) · 10s product hero · 5s end card |

First 2 seconds always the hook — product drop, macro texture, spotlight snap, unboxing reveal, direct address, "stop scrolling" moment. No exceptions.

---

## Motion vocabulary (the "dull-shot fix")

Static holds with only a rim-light breath read as AI slop. Every Seedance beat wants **purposeful motion**. Source: [higgsfield-seedance2-jineng skill library](https://github.com/beshuaxian/higgsfield-seedance2-jineng).

### 12 motion patterns that work

Each pattern is a short prompt phrase that reliably triggers clean cinematic motion in Seedance 2.0:

1. **Particle materialization** — "Product materializes from golden particles, coalescing from mist into perfect form." (Tech, luxury goods)
2. **Dramatic spotlight snap** — "Spotlight snaps on, product gleams in sharp light, shadow recedes." (Jewelry, watches)
3. **Crash & shockwave** — "Product crashes onto surface, shockwave ripples outward, comes to rest." (Durable/tough goods)
4. **Unwrap / peel reveal** — "Protective wrapping peels back, revealing pristine product beneath." (Unboxing)
5. **Macro-to-wide pull-back** — "Macro shot of [texture detail] pulls back, revealing full [product]." (Fashion, luxury)
6. **Self-assembly** — "Modular segments float and lock together, forming complete device." (Tech)
7. **Exploded-view snap-together** — "All components visible in space, rapidly snap into tight assembly." (Tech)
8. **Liquid pour / transparency bloom** — "Perfume fills bottle with color, liquid settles, light refracts through glass." (Beauty, beverages)
9. **Slow-motion lift** — "Product slowly lifts from surface, floating into smooth rotation." (Luxury, elegance)
10. **Spin-to-reveal (180°)** — "Half-rotation reveals embossed detail on back panel." (Reveals a hidden side)
11. **Zoom & pan transition** — "Camera dives into brushed metal surface, pulls back to reveal entire watch." (Material storytelling)
12. **Halo light flare** — "Brilliant light flare cascades across [surface], illuminating [feature]." (Jewelry, premium)

### Rotation speed ladder

| Speed | 360° duration | Use |
|-------|---------------|-----|
| Slow | 10-15s | Luxury, watchmaking, fragrance — viewer absorbs every detail |
| Medium | 5-8s | Fashion, cosmetics — form + function |
| Fast | 2-4s | Tech, dynamic — speed + modernity |
| Multi-speed | variable | Start slow on hero angle, accelerate for impact |

### Detail-progression template (e-commerce hero)

Build a visual narrative of discovery:

1. **Establish** — reveal product in hero context + lighting
2. **Hero angle** — most important ~45° view
3. **Rotation** — slow 360° across all sides
4. **Details** — macro shots of texture, stitching, seams
5. **Context** — product in use / lifestyle / packaged
6. **Close** — return to hero angle with light flourish

Don't shove all six into a 6-second clip. Pick 2-3, match to duration.

### What *not* to write (causes dull output)

- "Held static product shot. The camera does not move." → reads as still-life, no motion, AI slop
- "Over six seconds a rim light breathes slightly brighter" → no subject motion at all, weak
- "Exactly as in the reference, no reframing" → Seedance interprets this as a still-frame loop

**Instead**, every prompt should name:
- A **camera verb** (push in, pull back, rotate, lift, dive, drift)
- A **subject action or material change** (gleams, settles, catches light, tilts, flashes highlight)
- A **lighting evolution** (rim light sweeps, shadow recedes, halo flare)

Target at least two of the three in every beat.

### Worked example — hero product (Beat A style, 6s)

```
DULL (what we had):
"The camera does not move. Over six seconds a cold rim light breathes very
slightly brighter. The scene remains otherwise completely still."

LIVE (motion rewrite, from higgsfield vocabulary):
"Slow-motion lift and reveal. The matte-black serum bottle begins in shadow,
a single hard spotlight snaps on from camera-right at 0.5 seconds, the rim
light sweeps along the bottle's right edge from base to cap over three seconds,
a subtle halo flare cascades across the silver wordmark. The camera pushes in
by 10% from 2s to 6s, holding the silhouette centred. The plinth stays in shadow.
Cinematic jewelry lighting. Deep held low string tone, a single metallic shimmer
at the halo flare."
```

---

## Prompting Guide

### Core Syntax: Reference System (Ark API)

The Ark API uses positional references: "Image 1" / "Image 2" / "Video 1" / "Audio 1" map to the order you list them in the `content` array. In the prompt, refer to them naturally:

```
Use the first-person POV framing from Video 1 throughout, and use Audio 1 as the
background music throughout. Opening frame is Image 1, ... final frame freezes on
Image 2.
```

| Purpose | Syntax |
|---------|--------|
| First frame | `Image 1 as the first frame` |
| Last frame | `Image 2 as the last frame` |
| Character appearance | `Image 1's character as the subject` |
| Scene/background | `scene references Image 3` |
| Camera movement | `reference Video 1's camera movement` |
| Action/motion | `reference Video 1's action choreography` |
| Visual effects | `completely reference Video 1's effects and transitions` |
| Rhythm/tempo | `video rhythm references Video 1` |
| Voice/tone | `narration voice references Video 1` |
| Background music | `BGM references Audio 1` |
| Sound effects | `sound effects reference Video 3's audio` |
| Outfit/clothing | `wearing the outfit from Image 2` |
| Product details | `product details reference Image 3` |

### Multi-Reference Combo

```
Use Image 1's character as the subject, reference Video 1's camera movement
and action choreography, BGM references Audio 1, scene references Image 2.
```

### Prompt Structure

```
[Subject/Character Setup] + [Scene/Environment] + [Action/Motion] +
[Camera Movement] + [Timing Breakdown] + [Transitions/Effects] +
[Audio/Sound Design] + [Style/Mood]
```

### Time-Segmented Format (Recommended for 8s+ clips)

```
0-3s: Wide establishing shot, slow dolly forward along the street.
3-6s: Medium shot, character walks toward camera. Subtle head turn.
6-10s: Push-in to close-up, shallow depth of field. Rack focus to background.
```

Match prompt complexity to generation duration — don't overload 4-5s clips with too many scenes.

---

## Camera Language Reference

### Basic Movements
| Term | Description |
|------|-------------|
| Push in / Slow push | Camera moves toward subject |
| Pull back / Pull away | Camera moves away from subject |
| Pan left/right | Camera rotates horizontally |
| Tilt up/down | Camera rotates vertically |
| Track / Follow shot | Camera follows subject movement |
| Orbit / Revolve | Camera circles around subject |
| One-take / Oner | Continuous shot with no cuts |

### Advanced Techniques
| Term | Description |
|------|-------------|
| Hitchcock zoom (dolly zoom) | Push in + zoom out, creates vertigo effect |
| Fisheye lens | Ultra-wide distorted lens |
| Low angle / High angle | Camera below/above subject |
| Bird's eye / Overhead | Top-down view |
| First-person POV | Subjective camera from character's eyes |
| Whip pan | Very fast horizontal pan, creates motion blur |
| Crane shot | Vertical movement like crane arm |

### Shot Sizes
| Shot | Frame |
|------|-------|
| Extreme close-up | Eyes, mouth, or small detail only |
| Close-up | Face fills frame |
| Medium close-up | Head and shoulders |
| Medium shot | Waist up |
| Full shot | Entire body |
| Wide / Establishing | Full environment |

---

## Use Case Prompt Patterns

### 1. Character Consistency (Multi-Scene)
```
The man in Image 1 walks tiredly down the hallway...
maintaining consistent appearance throughout.
```

### 2. Camera Movement Replication
```
Reference Video 1's camera movements and facial expressions completely.
Hitchcock zoom during fear moment, then orbit shots.
```

### 3. Template / Effects Replication
```
Replace Video 1's character with Image 1.
Reference Video 1's camera work — close orbit shot
transitions from third-person to subjective POV.
```

### 4. Video Extension
```
Extend Video 1 by 15 seconds.
1-5s: Light slides across wooden table.
6-10s: Coffee bean drifts down slowly.
11-15s: Text appears gradually.
```
Set generation duration to match extension length.

### 5. Music Beat-Matching
```
Image 1 Image 2 Image 3
Match the keyframe positions and overall rhythm of Video 1
for beat-synced cuts.
```

### 6. E-commerce / Product Showcase
```
Deconstruct the reference image. Static camera.
Hamburger rotating mid-air. Ingredients gently separate
while maintaining shape. Cheese melts and drips.
```

### 7. Dialogue and Voice Acting
```
Cat host (licking paw, rolling eyes):
"Who understands my suffering?"
```
Include emotional direction in parentheses before dialogue.

### 8. One-Take / Long Take
```
Image 1 Image 2 Image 3 Image 4 Image 5
One-take tracking shot, following runner from street up stairs.
No cuts throughout.
```

### 9. Science/Educational Content
```
15-second health educational clip.
0-5s: Transparent blue human upper body, artery blood flows smoothly.
5-10s: Sugar particles enter bloodstream.
10-15s: Cross-section of artery, gradual narrowing.
```

---

## Style and Quality Modifiers

### Visual Style
- Cinematic quality, film grain, shallow depth of field
- 2.35:1 widescreen, 24fps
- Ink wash painting style / Anime style / Photorealistic
- High saturation neon colors, cool-warm contrast
- 4K medical CGI, semi-transparent visualization

### Mood/Atmosphere
- Tense and suspenseful / Warm and healing / Epic and grand
- Comedy with exaggerated expressions
- Documentary tone, restrained narration

### Audio Direction
- Background music: grand and majestic
- Sound effects: footsteps, crowd noise, car sounds
- Voice tone reference Video 1
- Beat-synced transitions matching music rhythm

---

## Common Mistakes to Avoid

| Mistake | Why | Fix |
|---------|-----|-----|
| Vague references | "Image 1" without specifying WHAT to reference | Always say camera? action? effects? appearance? |
| Conflicting camera | "static camera" AND "orbit shot" | Pick one movement per time segment |
| Overloading short clips | Too many scenes in 4-5s | Match complexity to duration |
| Missing role assignments | Uploaded files unused | Every reference needs a role (reference_image/video/audio) |
| Ignoring audio | Sound design dramatically improves output | Always include audio direction |
| Wrong duration | Prompt complexity doesn't match selected length | More detail for longer clips |
| Real faces | System blocks photorealistic faces | Use 3D/stylized, products, or switch to LTX/Veo |

---

## Post-Processing (REQUIRED)

All Seedance outputs are **Variable Frame Rate (VFR)**. MUST convert to CFR before editing or concatenation:

```bash
ffmpeg -y -i input.mp4 -r 24 -vsync cfr -c:v libx264 -preset fast -crf 18 -an output_cfr.mp4
```

---

## Workflow: Step-by-Step

1. **Clarify goal:** Video type (ad, drama, MV, educational, vlog)?
2. **Check face policy:** Does it need photorealistic faces? If yes, use LTX or Veo instead.
3. **Identify assets:** What images, videos, audio are available?
4. **Upload to S3 (or pre-hosted):** Ark requires fetchable HTTPS URLs. The script auto-uploads locals via `media_host.py` when `S3_BUCKET` is set.
5. **Assign roles:** Map each asset to function (first frame, char ref, camera ref, etc.)
6. **Structure prompt:** Subject/scene -> Time-segmented descriptions -> Camera -> Audio -> Style
7. **Check constraints:** Total files ≤12, no real faces, durations within limits.
8. **Generate:** `python scripts/generate_video_seedance.py ...`
9. **Post-process:** Convert VFR to CFR with ffmpeg.

---

## Comparison with Other Models

| Feature | Seedance 2.0 (Ark) | Veo 3.1 | LTX 2.3 |
|---------|-------------------|---------|---------|
| Human faces | BLOCKED | Works | Works |
| Max duration | ~12s | 8s | 20s |
| Resolution | ~720p | Up to 4K | Up to 2160p |
| Reference images | Up to 9 | Up to 3 | 1 (+ end image) |
| Positional references | Image 1 / Video 1 / Audio 1 | No | No |
| Time-coded prompts | Native | Timestamp syntax | Natural language |
| Camera replication | From reference video | N/A | N/A |
| Audio sync | `generate_audio` + BGM ref | Built-in | Audio-to-Video endpoint |
| Post-processing | VFR->CFR required | Ready to use | Ready to use |
| Face blocking | YES | No | No |
| Best for | Products, 3D chars, effects replication | Quality, faces | Budget, long clips |

---

## Tested Examples

### Example: Quilted Leather Texture (Ark, 8s)
- **Input:** `https://pub-a836d08629454caf9059acebd385a714.r2.dev/chanel-ad/scene_01_texture.png`
- **Prompt:** "Camera slowly drifts across quilted black leather surface. Light catches gold chain hardware. Luxury product macro shot, shallow depth of field."
- **Result:** `bags-ad/v2/seedance/texture_test.mp4` (3.6 MB)
- **Status:** Success (no faces = no blocking)

### Example: 3D Street Walk (Ark, 8s)
- **Input:** `https://pub-a836d08629454caf9059acebd385a714.r2.dev/chanel-ad/char_3d_street.png`
- **Prompt:** "3D animated woman walks down a Parisian street, Pixar style. Carrying a quilted handbag. Camera tracks alongside."
- **Result:** `bags-ad/v2/seedance/sd_01_street.mp4` (3.4 MB)
- **Status:** Success (3D style bypasses face filter)

### Example: Photorealistic Face (Ark) — BLOCKED
- **Input:** `char_ref.jpg` (AI-generated face from Veo)
- **Status:** `content_policy_violation` — blocked even though face was AI-generated
- **Learning:** ANY photorealistic face gets blocked, real or AI

<!--
ADD MORE EXAMPLES:

### Example: [Name] ([access method], [duration])
- **Input:** [URL or description]
- **Prompt:** "..."
- **Result:** [path] or BLOCKED
- **Status:** Success / Blocked / Notes
- **Learning:** [what to do differently]

PATTERNS NEEDING EXAMPLES:
- [ ] Video extension
- [ ] Camera movement replication from @Video reference
- [ ] Beat-matching with @Audio reference
- [ ] Multi-reference combo (char + scene + camera)
- [ ] Product showcase / e-commerce
- [ ] One-take long shot
-->

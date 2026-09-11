# Nano Banana 2 -- Complete Image Prompting Guide

> **2026-09: Nano Banana is now the FALLBACK.** Default still model is GPT Image 2 — see `gpt-image.md` and `scripts/generate_image_gpt.py`. This script is `scripts/generate_image_gemini.py`.

> **2026-09 update — model ids.** `generate_image_gemini.py` aliases: `--model nb2` → `gemini-3.1-flash-image` (Nano Banana 2, GA, default; the `-preview` id still works),
> `--model pro` → `gemini-3-pro-image` (Nano Banana Pro — best likeness, typography and brand-text fidelity; use for hero stills, packaging, anything with words),
> `--model lite` → `gemini-3.1-flash-lite-image` (Nano Banana 2 Lite — cheapest, for coverage/variants). Run `python scripts/list_models.py --filter image` when in doubt.
> `--size` is ignored unless the installed `google-genai` exposes `ImageConfig.image_size` (1.47.0 does not).


Source: Google Cloud Blog "The ultimate Nano Banana prompting guide" + Google DeepMind prompt guide

## Models

| Model | API ID | Base | Speed | Text Rendering |
|-------|--------|------|-------|----------------|
| Nano Banana 2 | `gemini-3.1-flash-image-preview` | Gemini 3.1 Flash | Fast | Short words only |
| Nano Banana Pro | `gemini-3-pro-image-preview` | Gemini 3 Pro | Slower | Flawless sentences |

### Tech Specs

| Spec | Nano Banana 2 (3.1 Flash) | Nano Banana Pro (3 Pro) |
|------|---------------------------|------------------------|
| Input tokens | 131,072 max | 65,536 max |
| Output tokens | 32,768 max | 32,768 max |
| Resolutions | 512, 1K, 2K, 4K | 1K, 2K, 4K |
| Aspect ratios | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, 1:4, 4:1, 1:8, 8:1 | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| Object refs | Up to 10 | Up to 6 |
| Character refs | Up to 4 | Up to 5 |
| Total refs | Up to 14 | Up to 11 |
| Knowledge cutoff | January 2025 | January 2025 |
| Live data | Real-time web search | Real-time web search |
| Trust & safety | C2PA + SynthID watermark | C2PA + SynthID watermark |

### API Parameters

```python
config=types.GenerateContentConfig(
    response_modalities=["TEXT", "IMAGE"],  # MUST include IMAGE
    image_config=types.ImageConfig(
        aspect_ratio="16:9",   # any supported ratio
        image_size="2K",       # 512, 1K, 2K, 4K (uppercase K)
    ),
)
```

---

## The Five Prompting Frameworks

Nano Banana uses deep reasoning to understand your prompt before generating. Start with a strong verb that tells the model the primary operation.

### Framework 1: Image Generation

**Text-to-image (no references)**

Formula: `[Subject] + [Action] + [Location/Context] + [Composition/Camera] + [Style]`

Write like briefing a human artist. Full narrative sentences, not keyword lists.

```
[Subject] A striking fashion model wearing a tailored brown dress, sleek boots,
and holding a structured handbag.
[Action] Posing with a confident, statuesque stance, slightly turned.
[Location] A seamless, deep cherry red studio backdrop.
[Composition] Medium-full shot, center-framed.
[Style] Fashion magazine style editorial, shot on medium-format analog film,
pronounced grain, high saturation, cinematic lighting effect.
```

**Multimodal generation (with references)**

Formula: `[Reference images] + [Relationship instruction] + [New scenario]`

```
[References] Using the attached napkin sketch as the structure and the attached
fabric sample as the texture,
[Relationship] transform this into a high-fidelity 3D armchair render.
[New Scenario] Place it in a sun-drenched, minimalist living room.
```

Use this for:
- Character consistency (pass character ref + scene description)
- Product placement (pass product photo + new environment)
- Style merging (pass style reference + content description)
- Set continuity (pass location ref + new camera angle)

### Framework 2: Image Editing

**Conversational editing (without new references)**

Semantic masking (inpainting): Define a "mask" through text. Be explicit about what stays the same.

Template: "Using this image, remove the [specific element]. Keep everything else exactly the same, preserving the original style, lighting, and composition."

For replacement: "Remove the person and replace with a potted plant."

**Composition and style transfer (with new references)**

Adding elements: Upload base image + object image, tell model to combine them.
```
Place the product from the second image onto the table in the first image.
Match the lighting and perspective of the original scene.
```

Style transfer: Upload photo, ask to recreate in different style.
```
Recreate this exact city street scene in the style of a Van Gogh oil painting.
Keep the composition and perspective identical.
```

### Framework 3: Real-Time Web Search

Nano Banana can search the web for current data before generating.

Formula: `[Source/Search request] + [Analytical task] + [Visual translation]`

```
[Search] Search for current weather and date in San Francisco.
[Analyze] Use this data to modify the scene — if raining, make it grey and rainy.
[Visualize] Render this as a miniature city-in-a-cup concept embedded within
a realistic smartphone UI.
```

Use for: localized marketing, current events visualization, educational tools, travel apps.

### Framework 4: Text Rendering & Localization

Rules for sharp, legible text:

1. **Use quotes**: Enclose desired words in quotes — `"Happy Birthday"` or `"URBAN EXPLORER"`
2. **Choose a font**: Describe typography — `"bold, white, sans-serif font"` or `"Century Gothic 12px"`
3. **Specify material**: `"3D block letters with metallic gold texture, soft shadow"`
4. **Translate**: Write prompt in one language, specify target language for output
5. **Text-first hack**: First ask Gemini to generate the text concepts in conversation, THEN ask for image with that text

```
A high-end glossy beauty shot of a sleek face moisturizer jar on warm studio background.
Soft radiant lighting. Render three lines of text with exact styling:
Top line: 'GLOW' in flowing Brush Script font.
Middle: '10% OFF' in heavy Impact font.
Bottom: 'Your First Order' in thin Century Gothic font.
Then translate the text into Korean and Arabic.
```

```
A typographic poster with a solid black background, bold letters spell "New York",
filling the center of the frame. The text acts as a cut-out window.
A photograph of New York skyline is visible ONLY inside the letterforms.
```

### Framework 5: Prompting Like a Creative Director

Stop typing keywords. Start directing the scene.

**1. Design your lighting**

| Technique | Prompt Language |
|-----------|----------------|
| Studio product | "Three-point softbox setup" |
| Dramatic/moody | "Chiaroscuro lighting with harsh, high contrast" |
| Warm/romantic | "Golden hour backlighting creating long shadows" |
| Soft/flattering | "Soft natural light from a north-facing window" |
| Atmospheric | "Tyndall effect — visible light beams through particles" |
| Edge definition | "Rim light from behind, silhouetting the subject" |
| Volumetric | "God rays through dusty atmosphere" |

**2. Choose your camera, lens, and focus**

| Hardware | Effect |
|----------|--------|
| `GoPro` | Immersive, distorted, action feel |
| `Fujifilm` | Authentic color science |
| `cheap disposable camera` | Raw, nostalgic flash aesthetic |
| `medium-format analog film` | Pronounced grain, rich tonality |
| `f/1.8 lens` | Extreme shallow depth of field |
| `wide-angle 10mm` | Vast scale, distortion |
| `macro lens` | Intricate details |

**3. Define color grading and film stock**

| Mood | Prompt Language |
|------|----------------|
| Nostalgic/gritty | "As if on 1980s color film, slightly grainy" |
| Modern moody | "Cinematic color grading with muted teal tones" |
| Warm vintage | "Warm sepia with faded edges, Polaroid aesthetic" |
| Cool cinematic | "Teal-and-orange color grade, blockbuster feel" |
| Vibrant anime | "Vibrant anime palette, high saturation" |

**4. Emphasize materiality and texture**

Don't say generic — say specific:

| Bad | Good |
|-----|------|
| "suit jacket" | "navy blue tweed suit jacket" |
| "armor" | "ornate elven plate armor, etched with silver leaf patterns" |
| "mug" | "minimalist ceramic coffee mug, matte white glaze" |
| "dress" | "flowing emerald silk dress with subtle sheen" |
| "leather" | "worn saddle leather with visible grain and patina" |

---

## Golden Rules

1. **Use natural language, full sentences** — write like briefing a human artist, not keyword soup
2. **Be specific** — concrete details on subject, lighting, composition
3. **Use positive framing** — "empty street" not "no cars"
4. **Control the camera** — "low angle", "f/1.8", "macro lens"
5. **Iterate conversationally** — edit and refine, don't re-roll from scratch
6. **Emphasize materiality** — specific fabrics, surfaces, textures
7. **Start with a strong verb** — tells the model the primary operation

---

## Camera & Shot Types

### Basic Shots
- Close-up, Medium shot, Full shot, Long shot
- Bird's eye view / top-down
- Low-angle view, Eye-level, High-angle
- Full body portrait, Profile portrait

### Creative Shots
- Drone view / top-down drone perspective
- POV (point of view)
- Macro lens, Fisheye lens
- Tilt-shift (miniature style)
- Extreme close-up, Worm's-eye view
- Wide-angle / fisheye (10mm-14mm)
- Dramatic ultra-wide low-angle

---

## Composition

| Technique | Prompt Language |
|-----------|----------------|
| Rule of thirds | `rule of thirds composition` |
| Centered symmetrical | `centered, symmetrical framing` |
| Leading lines | `leading lines draw eye to subject` |
| Framing | `framed through doorway/window` |
| Negative space | `generous negative space around subject` |
| Depth of field | `shallow depth of field, f/1.8, blurred background` |
| Deep focus | `deep focus, f/11, everything sharp` |
| Split composition | `multi-angle product shots` |

---

## Style Keywords

### Artistic Styles
Flat illustration, Impressionist oil painting, Watercolor, Charcoal sketch, Ukiyo-e, Ink wash, Impasto, Manga illustration, Vector art, Pixel art, Voxel art, Post-Impressionism, Doodle/line art, Hand-drawn

### 3D/Digital
3D render, C4D render, Octane render, Claymation style, 3D embossed glossy contour

### Photography & Film
B&W photography, Cinematic, Polaroid, Documentary photography, Photorealistic, Ultra-realistic, Editorial photography, Film grain texture

### Genre Styles
Ghibli style, Cyberpunk, Vaporwave, Norse mythology, Rococo art, Fashion magazine, Retro-futuristic, 1999 hacker aesthetic, Modern minimalist

---

## Quality Keywords

`masterpiece, high quality, incredible details, 8K, ultra-high detail, sharp focus, fine film grain, pixel-perfect, hyper-realistic, professional, award-winning`

---

## Color & Mood

`muted warm tones, pastel palette, teal-tinted fog, vibrant anime palette, cinematic teal-and-orange grade, neon cyan glow, moody ethereal atmosphere, high saturation, cold overcast, dramatic teal and magenta`

---

## Character Consistency

### Identity Locking
Explicitly instruct: **"Keep the person's facial features exactly the same."**

### Reference Image Method (recommended for films)
1. Generate 1:1 reference portrait with neutral background
2. Pass this portrait as first content item in every scene prompt
3. Include identical Character Lock Block text description every time
4. Prepend: "Use the attached reference image. Keep facial features, hair, and build exactly the same."

### Set/Location Consistency
Same technique as characters — generate a location reference image and pass it into every scene at that location:
1. Generate 16:9 wide shot of the full set with clear lighting
2. Generate 16:9 close-up of key surfaces (workbench, desk)
3. Pass these as refs alongside character refs (up to 14 total)
4. Include identical Set Lock Block text description every time

### Multi-Image Storyboarding
- Generate sequential art in a single session
- Maintain character identity/attire across frames
- Vary angles, distances, expressions
- Pass ref images for consistency across sessions

---

## Character Sheet Generation — the canonical prompt

**Who this is for:** anyone building a film or commercial who needs the same character across many scenes. Nano Banana 2 handles this better than third-party "character ID" services **when given the right prompt** — no Soul ID, no proprietary tools required.

**Protocol:**

1. Start with ONE usable reference image of the character (a Seedream generation, a real photo, a Nano Banana t2i you liked).
2. Feed it to Nano Banana 2 via `--ref <ref>` with the canonical sheet prompt below.
3. Output is a single 2K image containing all 7 canonical panels in a 2-row grid.
4. Save as `refs/character_sheets/<name>.png`.
5. For every subsequent scene, attach the sheet as `--ref` alongside the location sheet. Include the character lock block in the text prompt. Every scene now has locked casting.

### Canonical character-sheet prompt (Nano Banana 2)

```
Using the attached reference image as the single source of truth for facial
features, hair, skin tone, and body proportions — generate a professional
character reference sheet for consistent use across a film production.

LAYOUT (strict):
Two horizontal rows against a clean neutral plain background (light grey #E8E8EA).
TOP ROW — four full-body views of the same person in identical wardrobe, identical
pose variations, even spacing:
  Panel 1: front, facing camera, arms relaxed at sides
  Panel 2: left profile, 90° side view
  Panel 3: right profile, 90° side view
  Panel 4: back, facing away
BOTTOM ROW — three head-and-shoulders portraits, neutral expression:
  Panel 5: front, eyes to camera
  Panel 6: left profile head
  Panel 7: right profile head

IDENTITY LOCK: Every panel shows the exact same person from the reference —
identical face shape, identical eye shape and colour, identical nose, identical
mouth, identical hairline and hair colour and hair style, identical skin tone
and freckles and moles, identical body proportions. DO NOT invent new features.
DO NOT stylise. Any drift = failure.

WARDROBE LOCK: Identical outfit across all 7 panels, matching the reference
image exactly. Same garments, same colour, same fit.

LIGHTING: Identical across every panel — soft three-point studio lighting at
5500K. No hard shadows. No coloured gels. Even exposure on face and body.

EXPRESSION: Neutral across all panels — mouth closed, no smile, no frown.
Eyes open. Calm, resting face. No head tilt.

TECHNICAL: Ultra-realistic, print-ready reference sheet. Shot on a Hasselblad
H6D 100C equivalent, sharp focus, clean skin texture with natural pores, no
beauty retouching, no glamour, no makeup that wasn't on the reference. Match
the film stock and colour grade of the reference image.

Do not write text on the image. No subtitles, captions, labels, or numbering.
```

**CLI usage:**

```bash
python scripts/generate_image_gemini.py \
    --prompt "<paste the sheet prompt above>" \
    --ref ~/Desktop/project/refs/char_source.png \
    --aspect 16:9 \
    --output ~/Desktop/project/refs/character_sheets/sofia.png
```

**When to rerun:** if the output drifts on any panel (wrong nose, missing freckles, wardrobe swap), regenerate with the same ref. Nano Banana 2 is stochastic — expect 1-3 attempts to get a sheet where all 7 panels lock.

**Multi-character sheet:** when two or more characters appear together in the film, you can generate a second "pair sheet" — same 7-panel layout but with both characters in each panel, confirming their relative height, proportions, and how they read side-by-side.

---

## Location Sheet Generation — the canonical prompt

**Protocol:**
1. Start with ONE usable reference image of the location.
2. Feed to Nano Banana 2 via `--ref` with the canonical location-sheet prompt.
3. Output is a single 2K image with 4 coverage angles + 3 detail close-ups.
4. Save as `refs/location_sheets/<location>.png`.
5. Attach to every scene prompt in that location.

### Canonical location-sheet prompt (Nano Banana 2)

```
Using the attached reference image as the single source of truth for the
location's architecture, materials, lighting, and colour palette — generate
a professional location reference sheet for consistent use across a film
production.

LAYOUT (strict):
Two horizontal rows against black separators between panels.
TOP ROW — four coverage angles of the same location, same time of day, same
weather, same lighting direction:
  Panel 1: straight-on frontal wide shot, centre of the space
  Panel 2: left-angled wide shot, 30° from frontal
  Panel 3: right-angled wide shot, 30° from frontal
  Panel 4: reverse wide, looking back the other way from the far side
BOTTOM ROW — three detailed close-ups of key environmental elements visible
in the reference:
  Panel 5: [key material or texture — e.g. stone counter, tile, floorboards]
  Panel 6: [key lighting source — e.g. window, lamp, skylight]
  Panel 7: [key prop or fixture — e.g. tap, shelf, chair]

LOCATION LOCK: Every panel shows the exact same location — same architecture,
same walls, same flooring, same ceiling, same fixtures, same props. DO NOT
invent new rooms. DO NOT move windows or doors.

ATMOSPHERE LOCK: Identical across every panel — same time of day, same
weather, same light direction, same shadow length, same colour temperature,
same mood.

LIGHTING: Match the reference exactly. If the reference has cool north-window
light at 5500K, every panel shows the same. No added fill, no studio lights.

PEOPLE: None. No person in any panel. Location only.

TECHNICAL: Ultra-realistic, print-ready location reference sheet. Preserve the
film stock and colour grade of the reference image.

Do not write text on the image. No subtitles, captions, labels, or panel numbers.
```

Replace the bracketed placeholders in Panels 5-7 with the specific props/materials/light sources visible in your reference.

---

## Workflow: Nano Banana sheets → Seedream/Seedance downstream

For projects that need AI-generated video of faces via Seedance:

1. **Nano Banana 2** produces the character sheet (7 panels, highest fidelity).
2. **Seedream 5.0 text-only** — re-prompt the character in-scene using the Nano Banana sheet as conceptual reference (NOT as `image` ref — that pushes Seedream outputs past Seedance's filter threshold). Describe the character verbally, matching the sheet's visual details.
3. **Seedance 2.0** consumes the Seedream scene still as the first-frame reference.

The Nano Banana character sheet never enters the video-gen pipeline directly — it's the human-readable anchor that keeps prompt-writing consistent across scenes. Think of it as the "bible" for the film's casting.

Skip the Seedream step (Nano Banana → Seedance direct) only if you're NOT using Seedance — Seedance's filter will reject Nano Banana photoreal faces. LTX 2.3 and Veo 3.1 accept them directly.

---

## Editing Strategies (Conversational)

1. **Change character** — swap subjects, keep style/setting
2. **Adjust composition** — new angle with perspective-specific details
3. **Alter action** — modify what characters do
4. **Swap setting** — transform environment
5. **Rethink style** — switch between photo/illustration/cartoon
6. **Maintain consistency** — upload refs and assign distinct names
7. **Add elements** — upload base + object, combine them
8. **Transfer style** — recreate content in different artistic style

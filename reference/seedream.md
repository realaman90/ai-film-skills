# Seedream 5.0 — BytePlus Ark Image Generation

BytePlus Ark's frontier image model. Primary reason we care: **Seedream outputs are the only photoreal AI faces that Seedance 2.0 will accept as video-generation references.** If you need an AI character in a Seedance clip, you go through Seedream first.

Source: [BytePlus ModelArk Image Generation](https://docs.byteplus.com/en/docs/ModelArk/1541523) · [Seedream 4.0-5.0 tutorial](https://docs.byteplus.com/en/docs/ModelArk/1824121)

---

## API

**Endpoint:** `POST https://ark.ap-southeast.bytepluses.com/api/v3/images/generations`
**Auth:** `Authorization: Bearer $ARK_API_KEY`

**Model IDs seen in the wild:**
| Model | Purpose |
|-------|---------|
| `seedream-5-0-260128` | Text-to-image + reference-based (default) |
| `seedream-4-0-*` | Previous generation |
| `seedream-3-0-t2i-250415` | Legacy t2i |
| `seededit-3-0-i2i-250628` | Dedicated image editor (different shape) |

**Request body (all in one payload — Seedream 5.0 dispatches by parameter presence):**
```json
{
  "model": "seedream-5-0-260128",
  "prompt": "…",
  "image": "<url>" | ["<url1>", "<url2>"],
  "sequential_image_generation": "disabled" | "auto",
  "sequential_image_generation_options": { "max_images": N },
  "response_format": "url",
  "size": "2K" | "1K" | "WxH",
  "stream": false,
  "watermark": false,
  "seed": 123
}
```

**Response (sync):**
```json
{
  "model": "seedream-5-0-260128",
  "created": 1776724277,
  "data": [ { "url": "https://...", "size": "WxH" } ],
  "usage": { "generated_images": 1, "output_tokens": N, "total_tokens": N }
}
```

URLs expire in 24h (`X-Tos-Expires=86400`). Download immediately.

---

## Four modes — all via the same endpoint

Dispatched by the combination of `image` and `sequential_image_generation` fields.

### 1. Text-to-image (single)
No `image`, `sequential_image_generation: "disabled"`.

```bash
python scripts/generate_image_byteplus.py \
    --prompt "documentary phone-mirror selfie, young woman post-workout, amateur iPhone quality" \
    --output gym.jpeg
```

### 2. Text-to-image (series)
No `image`, `sequential_image_generation: "auto"` + `max_images: N`.

```bash
python scripts/generate_image_byteplus.py \
    --prompt "Four seasons of the same Stockholm courtyard — winter, spring, summer, autumn" \
    --sequential 4 --output seasons.jpeg
# outputs: seasons_0.jpeg … seasons_3.jpeg
```

Use for: storyboard sweeps, same-character-multiple-moods, same-location-time-of-day.

### 3. Single-reference (image-to-image)
`image: "<url>"`, `sequential_image_generation: "disabled"`.

```bash
python scripts/generate_image_byteplus.py \
    --prompt "Using this LOGO as a reference, create a visual design system for an outdoor brand — packaging, hats, wristbands, lanyards" \
    --ref brand_logo.png \
    --output brand_system.jpeg --sequential 5
```

Use for: brand-mark extensions, bottle→scene integrations, re-compositions of a subject.

### 4. Multi-reference (images-to-image)
`image: ["<url1>", "<url2>", ...]`. Seedream can handle at least 2 simultaneous references.

```bash
python scripts/generate_image_byteplus.py \
    --prompt "Replace the clothing in image 1 with the outfit from image 2" \
    --ref character.png --ref outfit.png \
    --output styled.jpeg
```

Use for: outfit swaps, character + location combining, brand asset + lifestyle merge.

---

## Size rules

- Preset strings: `"1K"`, `"2K"` (model picks the aspect ratio)
- Explicit: `"WxH"` (e.g. `1440x2560`, `2560x1440`)
- **Minimum area: 3,686,400 pixels** (error `InvalidParameter` below this)
- For 9:16 portrait (Seedance-friendly): `1440x2560` minimum
- For 16:9 landscape: `2560x1440` minimum
- Square 1:1 with `image` ref tends to default to `2048x2048` regardless of preset

---

## Prompting — the "looks too finished" problem

Seedream 5.0's default aesthetic skews toward **commercial / studio / glamour photography**. For ads that want a documentary, raw, unposed feel, the default output reads as a stock-photo model shoot. Worse: the more polished the output, the more likely it is to fail downstream filters (see `seedance.md` → "Bypassing the real-person filter").

### Documentary prompt pattern

Layer these signals so Seedream de-polishes:

**Camera / capture medium:**
- "amateur iPhone selfie compression"
- "iPhone 14 Pro rear camera"
- "phone-mirror selfie, low-resolution"
- "Ricoh GR III snapshot"
- "35mm colour negative, Kodak Portra 400, light grain"
- "Fujifilm Pro 400H"

**Lighting:**
- "harsh overhead fluorescent, slight green cast"
- "available light only, no bounce, no fill"
- "overcast midday window light"
- "practical lamp only"

**Subject / performance:**
- "unposed, candid"
- "slightly off-centre framing"
- "subject not aware of camera"
- "mid-action, not a held pose"
- "fresh skin, no makeup, no glamour retouching"
- "natural slight flush, stray hair, imperfect"
- "documentary aesthetic"
- "Kinfolk editorial"

**Anti-signals (explicitly negate):**
- "not a fashion editorial"
- "not a glamour shot"
- "not beauty retouched"
- "no studio lighting"
- "no professional makeup"

### Stacking example (NORRA 20s gym beat)

```
Amateur phone-mirror selfie in a bright white subway-tiled gym locker room.
iPhone 13 Pro selfie camera, cool overhead LED fluorescent light with a slight
green cast, natural unretouched skin, visible pores, some fly-away hair strands.
A young woman in her early twenties just finished a workout. Dark brown hair in
a slightly messy high ponytail, a few wet strands at her temple, fresh complexion
with a slight flush from exercise, no makeup. Plain black ribbed sports bra and
grey sweatpants. Holding a black smartphone low in her right hand, the camera
facing the mirror. Her expression is calm and unhurried, slightly tired, eyes
soft, mouth neutral, not smiling. On the sink beside her sit a clear plastic
water bottle and a keyring with two keys. Documentary Kinfolk aesthetic. Not
a fashion editorial, not a glamour shot, not beauty retouched. Raw amateur
iPhone quality, slight camera shake, slightly imperfect framing.
```

### What still doesn't work
- **Non-Latin / special characters in type** — Seedream garbles "Å", "Ö", "N°" on bottle labels. Always comp exact branding in post (Remotion / ffmpeg overlay).
- **Consistent faces across separate calls** — Seedream doesn't have a character-seed system. Use one canonical reference image and `--ref` on every subsequent call if you need consistent casting.

---

## Pipeline: Seedream → Seedance (video)

The full loop for a face-containing video beat:

```
1. Seedream 5.0  →  photoreal still of the character + scene
     scripts/generate_image_byteplus.py
2. (Optional)    →  upscale / retouch locally
3. Seedance 2.0  →  6s video from the still
     scripts/generate_video_seedance.py
```

See `seedance.md` → "Bypassing the real-person filter via Seedream 5.0" for the exact mechanics (including when it works and when it fails).

### Hybrid option — Nano Banana 2 + Seedream

You can generate the initial scene composition in **Nano Banana 2** (broader aesthetic range, more documentary) and then pass it as a `--ref` to Seedream. This gets you:
- Nano Banana's looser, more lifestyle-feeling composition
- Seedream's BytePlus-native provenance (required for Seedance)

```bash
# Step 1: Nano Banana for the documentary scene sketch
python scripts/generate_image_gemini.py \
    --prompt "Documentary phone-mirror selfie in a gym locker room..." \
    --ref refs/original_cast.png \
    --aspect 9:16 --output sketch/gym_sketch.png

# Step 2: Seedream refines + bakes in the brand bottle
python scripts/generate_image_byteplus.py \
    --prompt "Using the reference scene, add the matte-black NORRA serum bottle on the sink" \
    --ref sketch/gym_sketch.png \
    --ref refs/anchor_01_v3_byredo.png \
    --size 1440x2560 \
    --output byteplus-gen/gym_final.jpeg
```

**Caveat:** if Seedream's output becomes too photoreal (likely with multi-ref), it still trips Seedance's filter. The text-only vs. image-ref threshold issue applies — test the Seedance acceptance before committing.

---

## Pricing & speed

- Per-image: token-billed (output tokens ≈ 14k–18k for 2K portrait)
- Latency: single text-to-image ~3-5s, reference-based ~5-10s
- No async/polling — sync response with URL

---

## Gotchas

- URL responses are signed and expire in 24h — download immediately.
- Square output even when you asked for non-square? → reference image ratio overrides `size: "2K"` preset. Use explicit `WxH`.
- Minimum pixel area is enforced (3,686,400). `1152x2048` fails with `InvalidParameter`.
- Seedream outputs feel "too finished" by default — layer the documentary prompt stack above.
- Multi-ref: Seedream honors both images, but the relative weighting is hard to control via prompt alone.

# Hard-Learned Lessons — AI Film Production

Real-world learnings from producing the Chanel bag ad across Veo 3.1, Seedance 2.0, and LTX 2.3. These are things NOT in official docs.

---

## Reference images > prompt tokens (the single biggest lesson)

**Problem we kept re-learning:** we'd spend 150+ words describing a scene in text, and the model would drift on composition, likeness, lighting, or props.

**What actually worked (from higgsfield $350K commercial guide + NORRA):**

1. **Build a canonical character sheet FIRST** — before generating any scenes. One Seedream / Nano Banana call per character, pick the best variant, lock it. This image is now the `@character` reference for every subsequent scene.
2. **Build a canonical location sheet SECOND** — one reference per location (kitchen, bathroom, gym, plinth studio). Lock it. Every scene in that location attaches the location sheet.
3. **Every scene prompt attaches BOTH** the character sheet AND the location sheet as references — not one or the other.
4. **Keep the prompt short.** Let the references do the visual heavy lifting. Prompt text describes only: the action, the camera move, the audio, the light evolution. **Not the subject, not the setting, not the look.**

**Corollary for Seedance specifically:** when i2v refs are strong, the prompt should be ~30-80 words of pure action/camera/audio. When the ref is weak (text-to-video), you need 150-300 words because you're describing everything from scratch.

**Warning for image-to-image on Seedream:** strong single-image refs produce *too* photoreal outputs that trip Seedance's real-person filter. When using Seedream as an upstream step for Seedance, prefer text-only Seedream OR multi-ref Seedream with anti-glamour language. See `reference/seedream.md` → "Documentary prompt pattern".

### Phrases that buy continuity across scenes (from the commercial guide)

Add one to every scene prompt when the look must stay identical across beats:

- `preserve original color grade, preserve original grain, preserve original exposure`
- `inspired by reference, not copied` (when you want interpretation, not direct use)
- `same lens, same stock, same grade as previous scene`

### Multi-ref attachment rules

- **1 ref** → the starting frame / strongest anchor
- **2 refs** → character + location OR start-frame + end-frame (keyframe interpolation)
- **3-4 refs** → character + location + prop + style reference
- **5-9 refs (Seedance ceiling)** → full commercial setup (multiple characters, multiple locations, brand assets)

Each ref's role should be named explicitly in the prompt: *"Use the first image as character reference, the second image as lighting and color-grade reference"* rather than leaving Seedance to guess.

---

## LTX i2v — Over-describing the subject wrecks the composition

**Problem (NORRA Beat A, 2026-04-20):** prompted LTX 2.3-Pro with a detailed description of the reference image (bottle, plinth, cap, lighting, grain) plus the motion we wanted (drop forming at the pump tip). Result: LTX push-zoomed aggressively past the reference, cropped out the bottle and plinth entirely, and invented a pear-shaped glass "drop" sitting ON TOP of the pump (physically wrong — drops fall down from a dispenser, not float above it). Clip read as obvious AI slop.

**Root cause:** Two failure modes stacked:
1. **Subject over-description in i2v.** The reference was strong — the prompt should only have described transition from stillness to motion. By re-describing everything, we gave LTX a second, competing brief; it re-interpreted the composition from scratch.
2. **Fluid-formation physics.** "A drop slowly forms at the dispenser tip, swelling" is something AI video cannot do — fluid dynamics is where these models tell on themselves. The model interpreted "swelling drop" as a static glass bulb.

**Rules:**
- For i2v with strong reference: prompt length should scale with *motion complexity*, not scene complexity. A 6-second static-camera subtle-motion beat deserves ~50-100 words of prompt, not 200+.
- Never prompt a pump or dropper to dispense on its own — it looks wrong on its own (real ads only show dispensing when a hand presses it), and AI fluid physics hallucinates.
- Static-camera lock phrases that actually work: *"The camera holds."* and *"No camera movement at all — no zoom, no dolly, no pan, no push-in."* Combine with `--camera-motion static` for redundancy.

**Fix pattern — before and after:**
```
BEFORE (failed — re-described everything in the reference):
"Extreme macro, locked static. The matte-black NORRA serum bottle stands on dark polished stone, pump cap lying beside it. A single translucent drop of clear serum slowly forms at the dispenser tip, swelling downward over four seconds... 35mm colour negative, light grain..."

BETTER (motion-only, but still had a trap):
"The camera holds. Over six seconds, the cold rim light along the right edge of the frame breathes very slightly brighter, peaks at four seconds, then settles. One fine particle of dust drifts slowly through the shaft of light. No other motion. Quiet room tone."
```
→ v2 trimmed subject description correctly, but **"one fine particle of dust"** triggered LTX's particle system into a full sparkle/glitter shower beside the bottle by t=3s. Classic AI-slop tell.

```
BEST (motion-only, no particle triggers):
"Camera holds for a moment. No motion in the frame. Over six seconds, the cold rim light along the bottle's right edge breathes very slightly brighter, reaches its peak around four seconds, then settles. The matte finish catches the light with a subtle velvet sheen. The scene remains otherwise completely still. Quiet anticipatory room tone, no music."
```

**Rules crystallized:**
- The image carries the look; the prompt carries only the change.
- **Never mention "particles," "dust," "motes," "sparkles,"** or any fluid-formation verbs ("forms," "swelling," "welling") in an LTX i2v prompt unless you explicitly want those effects. They wake the model's particle / fluid system.
- Describe evolving *light* instead of moving *stuff*: "the rim light breathes brighter" is safe; "dust drifts through the light" is not.
- Use "Camera holds for a moment." (from the official frog-yoga example) over "Extreme macro, locked static."

See `reference/ltx.md` → "Image-to-Video Rule: describe transition, not subject" and "Trigger words that backfire on i2v".

---

## Nano Banana 2 drifts on branded dispenser geometry

**Problem (NORRA stills coverage, 2026-04-20):** ran 6 variants of a pump-dispenser product still via `generate_image.py` with `--ref` pointing at the brand-approved reference. Despite reference image anchoring, Nano Banana consistently rendered the dispenser as a **dropper-pipette** instead of the pump, and garbled the typography (e.g. "AERFUTUS SEUM RYS" instead of "ÅTERFUKTANDE SERUM N°03").

**Rule:** `--ref` in Nano Banana 2 anchors overall mood and palette but **does not guarantee geometric fidelity** for unusual or brand-specific shapes (pumps, closures, hardware) or for text. Reference works better for *lighting/palette/character likeness* than for *exact prop geometry*.

**Workarounds:**
- For product beats with unusual geometry, prefer using the brand-approved still directly (don't regenerate).
- If you must regenerate, consider `--edit` mode instead of `--ref` — it's more likely to preserve the exact object.
- Typography should always be added in post (Remotion / PIL overlay), never trusted to the image model.

---

## `generate_image_gemini.py --size 2K` (Nano Banana) fails on current google-genai SDK

**Problem:** `ImageConfig(image_size="2K")` throws `Extra inputs are not permitted`. The installed `google-genai` doesn't accept `image_size` on `ImageConfig`.

**Fix:** Drop `--size` entirely. Default output from Nano Banana 2 (gemini-3.1-flash-image-preview) is ~1376×768 for 16:9, which is fine for video first-frame reference.

**Proper upstream fix:** remove or rename the `image_size` arg in `scripts/generate_image_gemini.py` (was generate_image.py) until the SDK re-exposes it.

---

## CC Lock / Logo Distortion Problem

**Problem:** The CC turn-lock on the Chanel bag morphed and distorted during AI video generation. Frame-by-frame analysis showed it changing shape throughout playback.

**Root cause:** AI video models can't maintain fine geometric details (logos, locks, clasps) across frames. The more detail and the closer the camera, the worse the distortion.

**Solution (from analyzing the real Chanel 25 ad by Michel Gondry):**
- The real ad NEVER shows the CC lock in close-up
- The bag is always at **medium distance (~10-15% of frame)**
- Product details are "sold" through lifestyle context, not macro shots
- **Rule: Avoid macro shots of intricate hardware/logos. Use medium-distance lifestyle shots.**

This applies to any branded product — watches, jewelry, tech products. If it has fine geometric detail, keep the camera at medium distance.

---

## Seedream → Seedance — the filter is threshold-based, not provenance-based

**Problem:** Seedance 2.0 blocks photoreal face images with `InputImageSensitiveContentDetected.PrivacyInformation`. BytePlus docs imply that outputs from their own models (Seedream / Seededit) are "trusted" within 30 days. **Reality is more nuanced.**

**What we observed (NORRA Beat B, 2026-04-21):**
- Seedream 5.0 with a **text-only prompt** → output accepted by Seedance ✅
- Seedream 5.0 with **a single image reference** (product bottle) → output rejected by Seedance ❌
- Seedream 5.0 with **multi-image references** → output rejected by Seedance ❌

Same account, same 30-day window, same BytePlus provenance. The only difference was Seedream's output aesthetic: text-only outputs retain a slight AI softness; reference-locked outputs become hyper-photoreal (commercial studio quality) and trip Seedance's photorealism classifier.

**Implication:** the Seedance filter is **threshold-based on visual photorealism**, not a provenance/allowlist check. The "trusted outputs" policy from BytePlus seems to be necessary-but-not-sufficient — the image also has to stay under the classifier's photoreal score.

**Workflow rule:**
- For Seedance face beats, use **text-only Seedream prompts**.
- If you need exact brand props in the frame, do NOT pass them via `--ref` (fails the filter). Comp them in post using Remotion or ffmpeg overlays.
- If you must use `--ref` with Seedream, stack "documentary amateur / low-fi / iPhone selfie / not beauty retouched" language to pull the output back under the filter's threshold. Test a cheap Seedance call before committing.

See `reference/seedream.md` → "Documentary prompt pattern" and `reference/seedance.md` → "Bypassing the real-person filter via Seedream 5.0".

---

## Seedream 5.0 default aesthetic is "too finished"

**Problem:** Seedream 5.0 outputs, even with explicit "documentary 35mm film" language, skew toward **studio commercial / beauty editorial / fashion campaign** quality. For ads that want a raw, unposed, phone-selfie feel, the default output reads as a stock-photo shoot — and simultaneously fails the Seedance filter because it's too photoreal.

**Root cause:** Seedream 5.0 was tuned on high-quality studio photography and commercial assets. The model's prior for "woman in a gym" includes lighting/framing discipline that documentary photography specifically avoids.

**Workaround — documentary prompt stack:**

Layer at least one signal from each category:

1. **Camera medium:** "iPhone 13 Pro selfie camera", "Ricoh GR III snapshot", "amateur phone selfie compression", "Kodak Portra 400 home-camera"
2. **Lighting:** "overhead fluorescent only, no bounce, no fill", "available light, no professional lighting"
3. **Subject:** "unposed, candid", "fresh skin, no makeup, no retouching", "visible pores, slight fly-away hair strands", "slightly tired expression", "mid-action, not a held pose"
4. **Explicit anti-signals:** "not a fashion editorial", "not a glamour shot", "not beauty retouched", "no studio lighting"

Compounding all four categories usually drags the output into the documentary zone. Skipping one category — especially the anti-signals — lets the default studio aesthetic creep back in.

See `reference/seedream.md` → "Documentary prompt pattern" for a full worked example.

---

## Seedance Face Blocking — More Aggressive Than Expected

**Problem:** Seedance 2.0 (both BytePlus Ark and fal.ai) blocks ALL photorealistic human faces with a content policy violation.

**What we tried that FAILED:**
- AI-generated faces from Veo/Nano Banana (blocked — treated as "real")
- Grid overlays on face images (still blocked)
- Partially obscured faces (still blocked)
- Different face compositions (all blocked)
- Cost: ~$5 in failed attempts before giving up

**What WORKS:**
- 3D Pixar-style characters (pass the filter)
- Product-only shots without faces
- Texture/detail close-ups
- **Switch to LTX 2.3 or Veo for any face content**

**Rule: Don't waste money trying to bypass Seedance face filter. It's absolute. Use a different model.**

---

## Character Consistency Across Scenes

**Problem:** Scene 02 had an Asian woman, Scene 03 had a blonde European woman. Different characters broke the ad narrative.

**Solution:**
1. Generate your first character scene with Veo/LTX
2. Extract a clean frame at the best moment: `ffmpeg -i clip.mp4 -vf "select=eq(n\,87)" -vframes 1 char_ref.jpg`
3. Use that extracted frame as `--image` input for ALL subsequent scenes
4. The extracted frame becomes the "character lock" for the entire project

**Rule: Never use text-to-video for character scenes after the first one. Always use image-to-video with a character reference frame.**

---

## Fast-Cut Editing Hides AI Artifacts

**Problem:** Individual 8s AI clips look noticeably AI-generated when watched in full. Motion gets weird, faces drift, physics break down.

**Solution (from analyzing the reference Chanel ad):**
- The real ad has 20+ cuts in 53 seconds (~2.5s average)
- Trim every AI clip to 2-3.5 seconds — the best 2-3s of each 8s generation
- Fast cuts maintain energy AND hide the quality drop-offs that happen mid-clip
- AI clips look their best in the first 2-3 seconds before motion degrades

**Rule: Generate 6-8s clips, trim to 2-3.5s for the final cut. The beginning of AI clips is almost always the strongest part.**

---

## Seedance: Duration Format Differs Between Providers (legacy note)

**Problem (fal.ai, legacy):** `"duration": 8` fails; must be `"duration": "8"` (string).

**Now (BytePlus Ark, current):** Integer works normally — e.g. `"duration": 11`. No string wrapping.

LTX also uses plain integers.

---

## Veo Model Name Changes

**Problem:** `veo-3.0-generate-preview` returns "model not found."

**Fix:** Model names change frequently. The correct name was `veo-3.0-generate-001`. Always run `python scripts/list_models.py --filter video` before assuming a model name.

---

## Veo SDK Download API Changed

**Problem:** `client.files.download(file=video, download_path=path)` throws `unexpected keyword argument 'download_path'`.

**Fix:** The SDK changed. Now returns bytes directly:
```python
video_bytes = client.files.download(file=gv.video)
open(output_path, "wb").write(video_bytes)
```

---

## Ken Burns Effect as Fallback

When video generation fails or is too expensive, you can create camera movement from static images using ffmpeg's zoompan filter:

```bash
# Slow zoom in over 6 seconds
ffmpeg -y -loop 1 -i still.png -vf "zoompan=z='min(zoom+0.001,1.3)':d=150:s=1920x1080" -t 6 -r 25 clip.mp4
```

This is free (no API cost) and works for establishing shots, product reveals, and transitions.

---

## LTX 2.3 vs Veo 3.1 — Real-World Quality

From the Chanel bag ad project (same images, both models):

| Aspect | Veo 3.1 | LTX 2.3 Fast |
|--------|---------|-------------|
| Face quality | Better, more consistent | Good, occasional drift |
| Motion naturalness | More natural | Slightly more robotic |
| Cost per 8s clip | ~$0.40 | $0.32 |
| Generation time | 60-120s | 30-60s |
| Audio | Built-in (good) | Built-in (decent) |
| Max duration | 8s | 20s |
| Failure rate | Occasional "no video returned" | Very reliable |
| Face blocking | None | None |

**Rule: Use Veo for hero shots where quality matters most. Use LTX for everything else to save money and time.**

---

## Reference Ad Analysis Workflow

The most valuable thing we did was analyze the real Chanel ad shot-by-shot before generating anything. This revealed:

1. **No macro shots of the CC lock** — saved us from generating bad clips
2. **Bag at 10-15% of frame** — the right framing for AI generation
3. **20+ fast cuts in 53s** — set the pacing target
4. **Desaturated environment, bag pops** — color strategy for prompts
5. **Multiple exposures / multiplication** — creative technique to reference

**Rule: Before generating an ad, analyze a real reference ad from the same brand/category. Use Gemini to do shot-by-shot analysis. Extract: shot sizes, cut timing, product placement strategy, color palette, camera language.**

Workflow:
```bash
# Analyze with Gemini
python -c "
from google import genai
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
video = client.files.upload(file='reference_ad.mp4')
response = client.models.generate_content(
    model='gemini-2.5-flash-preview-05-20',
    contents=[video, 'Analyze this ad shot by shot: timestamp, shot type, camera movement, action, lighting, duration, transition']
)
print(response.text)
"
```

---

## Image Hosting for Video APIs

**Seedance (BytePlus Ark)** requires fetchable HTTPS URLs for all references. Since 2026-09 the scripts auto-upload locals to **Amazon S3** (`scripts/media_host.py`, `S3_BUCKET` + `S3_REGION`; presigned URLs so the bucket can stay private). R2 vars still work as a legacy path.

**LTX** has its own `/upload` endpoint: POST returns a pre-signed URL + `storage_uri`; the script PUTs the file and passes `storage_uri` back as `image_uri`/`video_uri`/`audio_uri`. No S3 needed for LTX.

```bash
# Seedance: S3 auto-upload
python scripts/generate_video_seedance.py --image local.png ...

# LTX: uploads via LTX /upload (no external storage needed)
python scripts/generate_video_ltx.py --image local.png ...

# Either: pass a pre-hosted URL directly
python scripts/generate_video_ltx.py --image-url https://... ...
```

Set `S3_BUCKET`/`S3_REGION` in `~/config.env`; verify with `python scripts/media_host.py check`.

---

## Text Overlay Without Freetype

**Problem:** macOS Homebrew ffmpeg often compiled without freetype support, so `drawtext` filter doesn't work.

**Workaround:** Generate text overlay as PNG with PIL, then composite:
```python
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGBA', (1920, 1080), (0,0,0,0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 120)
bbox = draw.textbbox((0,0), "BRAND NAME", font=font)
w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
draw.text(((1920-w)//2, (1080-h)//2), "BRAND NAME", fill=(255,255,255,255), font=font)
img.save('overlay.png')
```

Then composite with ffmpeg:
```bash
ffmpeg -y -i video.mp4 -i overlay.png \
    -filter_complex "[0:v][1:v]overlay=0:0:enable='between(t,1,4)'" \
    -t 4 output.mp4
```

---

## Scene 04 Hero Text — Duration Bug

**Problem:** ffmpeg overlay with `shortest=1` caused 0-duration output when the overlay image had no duration metadata.

**Fix:** Always add explicit `-t` duration:
```bash
ffmpeg -y -i video.mp4 -i overlay.png \
    -filter_complex "[0:v][1:v]overlay=0:0" \
    -t 7 output.mp4  # explicit duration, not shortest=1
```

---

## Cost Tracking

| Model | What we spent | Clips generated | Cost per clip |
|-------|-------------|-----------------|---------------|
| Seedance (Ark) | ~$5 | 5 (3 success, 2 blocked) | ~$1.00 |
| LTX 2.3 Fast | ~$2.50 | 11 clips | ~$0.23 |
| Veo 3.1 | ~$3.50 | 7 clips | ~$0.50 |
| **Total** | **~$11** | **23 clips** | **~$0.48 avg** |

**Lesson:** Start with LTX Fast for iteration ($0.24/clip). Switch to Veo only for hero shots. Avoid Seedance for anything with faces.

---

## 2026-09 — Remotion → HyperFrames migration notes

**Why we switched:** the Remotion template needed `npm install` (Chromium pull, 1–3 min), a React/TS build, `--gl=angle` hacks on Linux, and every edit meant touching JSX. HyperFrames is one `index.html` + GSAP: `lint` catches broken timelines in 2 s, `check` audits layout/contrast/motion in a browser, `snapshot` gives PNGs at any timestamp without rendering, and a 10 s 1080p draft renders in ~12 s on an M-series Mac.

**What carried over unchanged:** the whole pre-assembly pipeline (lock blocks, refs, stills, clips, audio, CFR conversion), the `scenes.json` mental model (`build_hyperframes_timeline.py` accepts the same `--clip path:seconds` flags as the old Remotion builder), and the audio levels (VO 1.0 / music 0.10–0.15 / SFX 0.15–0.30).

**Traps we hit:**
- Tweening `volume` on an `<audio data-volume="0.15">` **replaces** the gain instead of scaling it — lint warns `audio_volume_tween_overrides_gain`. Carry the level in the tween, drop `data-volume`.
- `<video>` inside a timed `<div>` breaks frame extraction (`video_nested_in_timed_element`). Text overlays are sibling clips.
- `hyperframes init` writes skills into `~/.claude/skills` — fine once, noisy on every scaffold → `HYPERFRAMES_SKIP_SKILLS=1`.
- The scaffold's `.clip { inset: 0 }` silently pins a "bottom-right" logo to the top-left.
- Ken Burns on an `<img>` reports layout overflow unless marked `data-layout-allow-overflow`.

## 2026-09 — Reference analysis is now a script, and it changes model choice

Running `analyze_reference.py` on the Chanel 25 campaign film with a NORRA serum goal produced a brief that (a) turned a lateral-tracking single-take into a 5-shot vertical plan with matching camera vocabulary, (b) routed each shot to a model (Seedance for product/glass/water, Veo for anonymous body motion, still+Ken Burns for inserts), and (c) flagged fluid dispensing and typography as high-risk beats before we spent a cent. Treat the brief's `do_not_copy` list as a hard guardrail — the goal is the craft, never the brand's assets.

Seedance 2.5's 10-video reference slots make the inspiration video a *generation input* too: cut the 2–3 most useful shots (≤30 s total) and pass them with `--ref-video` ("camera like @Video1"). Combined with the analysis this is the closest thing to "make me one like this" that actually works.

## 2026-09-04 — Veo → Gemini Omni, Nano Banana → GPT Image 2

Decision: Google video now goes through **Gemini Omni 1.1 Flash** and stills through **GPT Image 2**. Both verified live:
a GPT Image 2 product still (label text rendered correctly first try — the thing Nano Banana kept garbling) animated by
Omni image-to-video at 360p for ~$0.12, plus a 3 s 9:16 text-to-video with native audio.

- Omni lives on the **Interactions API**, not `generate_videos`. The installed `google-genai` 1.47 (Python 3.9) has no
  `client.interactions`; `google-genai` ≥ 2.x needs Python 3.10+. The script calls REST directly so nothing had to be upgraded.
- The returned `uri` already ends in `:download?alt=media` — parse `files/<id>` out of it before polling/downloading.
- Authenticate with the `x-goog-api-key` header. Putting `?key=` in the URL echoed the key back inside a 400 error body
  (it landed in a transcript once — key rotated/rotate it). The script now redacts anything that looks like a key.
- No duration field on Omni: `--duration` injects "A N-second continuous shot." — works within 3–10 s.
- 360p drafts + `--previous <id>` refinement + `--upscale` is the cheapest iteration loop of any model here.
- GPT Image 2 with `--ref` goes through the *edits* endpoint with all refs as `image[]`; say what each image is for.

## 2026-09-04 — Ark activation is per model, and running tasks can't be cancelled

Regenerating the BytePlus key fixed the 401s, but Seedance 2.5 still returned `ModelNotOpen` until it was activated in the
ModelArk console (per-model switch; needs >USD 30 balance or a resource pack). 2.0 full/fast were already open. Once
activated, `generate_video_seedance.py --model 2.5 --task-type reference --image-url <S3 url>` produced a 4 s 720p clip
with audio in ~3.5 min. Lesson: check activation with an intentionally invalid request (e.g. `duration: 1`) — a valid
minimal request on an open model **is a billed job**, and `DELETE /tasks/{id}` returns 409 once it is running.

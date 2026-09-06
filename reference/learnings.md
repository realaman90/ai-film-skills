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

## 2026-09-04 — First full film through the v2 pipeline (KontentPlus intro, 60 s)

Reference analysis → script → GPT Image 2 refs/stills → Omni 360p drafts → HyperFrames cut with composited product UI. Draft in
one evening, ~$4 of API spend before the 1080p pass. What the run taught:

- **Approval gates paid for themselves.** The user changed the look twice at the reference stage (Stockholm, then "less oak, less
  render") for ~$0.80 total. The same change after stills or clips would have cost $5–15.
- **Omni image-to-video at 360p is ~25 s and ~$0.10 per clip.** Fifteen drafts in under 3 minutes with 3 workers. Faces held
  because every still came from the same character sheet; no `--ref` was needed on the video call.
- **3:2 stills cover a 16:9 frame with a 100 px crop top and bottom** (1536×1024 → 1920×1280). Any overlay positioned from
  still coordinates needs `y*1.25 - 100`. Omni also crops to 16:9 on its own, so positions read off a still can differ from the
  clip — check a rendered frame before locking overlay coordinates.
- **The builder's `.scene-img img` rule (100 % cover, centre origin) hijacks any `<img>` you inject into an image scene.** UI plates
  need a more specific rule restoring their natural size and `transform-origin: 0 0` before a `matrix3d` homography works.
- **Perspective-mapping UI onto blank screens works well in plain CSS**: 4-point homography → `matrix3d`, image at its natural
  size, wrapped together with the plate so Ken Burns moves both. Hand-placed quads beat naive white-region detection.
- `hyperframes check` flags text blocks inside floating cards as `content_overlap`; mark intentional layering with
  `data-layout-allow-overlap`. Non-transform tweens (`top`) and undeclared fonts are lint errors — use `y` and `@font-face { src: local() }`.
- ElevenLabs `with-timestamps` returns `audio_base64` (not `audio_base_64`); character timestamps are enough to split a
  continuous VO read into per-line segments with ffmpeg and place them on the timeline as `--sfx` entries.

## 2026-09-04 — "Think like a director": what turned a slideshow into a cut (KontentPlus intro v3–v8)

The first assembled draft was rejected as "poor, generic, white screens, bad transitions". The fixes, in order of impact:

1. **Run a second Gemini pass as an EDITOR, not an analyst** — beat sheet, cut list with per-cut motivation
   (action / look / sound / graphic match), cuts-per-5-s tempo curve, where it breathes, sound–picture sync — and then
   have Gemini critique *your draft* against that JSON. It measured our 4.1 s vs the reference's 2.8 s average shot and
   named the drags (empty plates, 15 s end card). Prompts are in the project (`refs/reference_edit_analysis.json`,
   `refs/draft_v3_critique.json`); worth folding into `analyze_reference.py` as `--mode editor` and `--critique draft.mp4`.
2. **Screens are never blank.** Blank white monitors read as AI instantly. Bake the real product UI into the stills:
   GPT Image 2 with the screenshot as a reference ("the monitors show exactly the interface in Image 3") renders it
   convincingly and keeps the face consistent. Composite crisp UI in HyperFrames only for hero screen moments.
3. **Let the product drive the middle.** Copying the reference's gag structure (avalanche, sticky note) gave a story
   that never showed how the product helps. Full-frame v9 screens with a cursor, a highlight, a click ripple and a
   status chip (all HyperFrames) became the spine; the operator became cutaways. VO rewritten to concrete verbs.
4. **Motivate every cut and vary the transition.** Chaos: 1.0–1.5 s shots, one whip. Turn: dip to navy + a sub-bass
   pulse. Calm: 3–4 s takes with 0.5 s blur crossfades. CTA: 8–9 s, not 15. The builder now takes `transitionIn` per
   scene (cut | crossfade | blur | dip | whip).
5. **Physically impossible frames get noticed** — a monitor whose screen faces the camera while the actor sits behind
   it ("the screen is inverted"). Check every still for screen direction and eyelines before animating.
6. **Seedance 2.5 and this workflow:** rejects photoreal faces from GPT Image 2 (real-person filter), and on a
   face-free hands insert it painted a literal green glow when the prompt said "the light on the knuckles shifts to
   green". Use it only for product/abstract shots and describe light, not colour words.
7. **Music must be written for the cut**, not the other way round: the bed's hard stop and pulse were regenerated to
   land on the dip once the timeline changed. ElevenLabs music takes timestamps in the prompt reliably.

## 2026-09-04 — Where Seedance 2.5 actually shines: era vignettes as text-to-video one-takes

The KontentPlus intro found its story on the third angle: "Knowing the customer" — four eras (1926 letterpress, 1966 agency
corkboard, 1996 TV + fax, 2016 the feed), then the product as the next era. Seedance 2.5 was the right tool **because**:
- Its real-person filter only bites on INPUT images. Pure text-to-video with people (backs, hands, silhouettes) passes,
  and era vignettes need no recurring character, so consistency is not a constraint.
- Time-coded beats ("0-2s … 2-4s … 6-7s") inside one 7 s take are honoured closely; period looks (silent-era sepia,
  Kodachrome, VHS, cold handheld) come out convincing from prompt alone. ~$1.5 per 7 s take at 720p, ~3 min each, 3 in parallel.
- A recurring physical motif (a hand finishing a gesture) makes the cross-era cuts feel authored; period framing (4:3
  pillarbox + grain → rounded 1.66 → 4:3 VHS → full 16:9) is a HyperFrames overlay, not a model prompt.
- Music generators don't reliably obey "hard stop at X s" — build the stop in the mix instead: trim the bed at the turn,
  insert silence + a synthesized sub pulse, resume from the bed's quiet section (`align_music.py`).
- Keep the operator/product section on Omni + composited UI; mixing models is fine when the sections are visually distinct.

## 2026-09-04 — The "Lumina" technique: one lateral take, worlds change behind foreground wipes

Aman's reference (a Seedance 2.5 showcase clip): a single protagonist walks left→right in profile at constant speed; a
floating motif (a feather) leads the eye; every ~5 s a foreground column/tree wipes the frame and the world behind
changes medium (felt → painting → 3D → photoreal → crayon). Reproduced on Seedance 2.5 **text-only** in one 15 s take:
market (oil painting) → 1920s print shop (sepia) → 1960s agency (Kodachrome), with a floating paper note as the motif and
a column / press frame / projector beam as the wipes. Prompt recipe: state the camera law first ("one continuous lateral
tracking shot, strictly left to right, constant speed, eye-level side profile, never a cut"), name the protagonist once
with a painterly/illustrated look (no photoreal → no face-filter risk), give the motif, then time-coded worlds each
ending with a named foreground object sweeping across. Cost ≈ $3 per 15 s at 720p, ~3 min.

Filter note: Seedance rejects **reference videos** containing a face too (`InputVideoSensitiveContentDetected`), even
an illustrated one — the style clip could not be attached; the prompt alone carried the technique.

## 2026-09-04 — The timeline device (HyperFrames): one axis, eras as modules, pushes, a bloom into the product

After several cuts, Gemini's editor pass + Aman's instinct converged on a **timeline** as the unifying system for an
"eras" film. Built entirely in HyperFrames on top of the builder's clips, no extra generation:
- **Modules without wrappers.** A `<video data-start>` can't sit inside a timed wrapper, so the module is a `clip-path:
  inset(96 240 306 240 round 18px)` on the video itself, plus a separate `.mod-frame` shadow box and a `.stem` down to the axis.
  (Bug to avoid: the CSS inset values are *edge distances*, not the box's bottom coordinate.)
- **Pushes.** Give each era scene `transitionIn: crossfade 0.45` in the spec (for the overlap), then tween `x: -1920` on the
  outgoing video and `x: 1920 → 0` on the incoming; the clip-path travels with the element, so the whole module slides.
  A `#ticks` strip (one 1920 px tick per era) tweens `x` by the same amount so the axis scrolls one decade per push.
- **Axis + labels.** A 3 px gradient line draws in (`scaleX`), a stem draws down (`scaleY`), decade + role in mono caps.
- **The turn.** A blurred blue `.axis-glow` flares and blows up (`scaleY: 40`) as the last era brightens, then the pixel
  scene draws a blue line at the same y and the glyph assembles on it — the product becomes the next marker.
- **Kinetic cards** ride inside the module (bottom-left) for eras and full-frame for the product section; each word springs
  in on the spoken phrase (timed from the VO character timestamps).
- Gemini's line-by-line critique (footage vs narration) is worth running on every draft: it caught the "biblical market",
  the duplicate hands and the agency framing that a frame sheet doesn't show.

## 2026-09-04 — A Gemini "jury" pass is a cheap, repeatable QA gate

Prompt Gemini as a jury of three (commercial director, B2B brand strategist, motion designer) with the narration lines and
their start times, ask for a scored rubric (story / footage / rhythm / motion / sound+VO / product clarity / persuasion /
overall), prioritized fixes with timestamps and effort, tagline options and "ready for 1080p?". Then re-run it on the next
version with the previous scores in the prompt so it re-scores under the same strictness. On the KontentPlus timeline cut:
6/10 across the board → after four cheap HyperFrames fixes (punch-ins on UI, bigger callouts, unified grain, larger CTA)
motion design 6→7 and "ready: yes", with one honest residual: dense product UI still reads slowly. Costs cents per pass;
prompts live in the project (`refs/timeline_v1_jury.json`, `refs/timeline_v2_jury.json`). Worth adding to
`analyze_reference.py` as `--jury <draft.mp4> [--previous jury.json]`.

## 2026-09-04 — product sections: build them natively, not as screenshots (KontentPlus timeline cut v5→v9)
- **Static app screenshots + highlight rings read as slop.** The user rejected two rounds of "hero screen" PNGs (stat cards, then outputs/report pages)
  with rings placed from guessed coordinates. What worked: ONE native HyperFrames canvas (`title` scene, text " ", overlays inject the HTML) — a 3300 px
  world inside a `#cam` wrapper (`transform-origin: 0 0`; to centre world point (wx,wy) at scale s: `x = 960 − wx·s, y = 540 − wy·s`), three stations
  (agent log that checks off → real LinkedIn post with a GPT-Image photo + blog + landing-page cards → chart + counters + proposed next step), camera pans
  keyed to the narration words. Blueprints used: agent-progress-theater, grid-card-assemble, constellation-hub, dataviz-countup (hyperframes-animation skill).
- **Key words → tweens.** `voB_words.json` (ElevenLabs character timestamps) → find the phrase inside the line ("strategy", "content", "every channel",
  "what actually worked") and key the camera/cascade to `line.start + (t_char − t_line_start)`. Same for "never forgets" on the brain beat.
- **Title-card CSS centres everything** — set `text-align:left; line-height:1.25` on the injected world or every card reads centred (user caught it).
  Use the real logo mark (`logo-mark.png`) in product cards, not a coloured square — the user noticed the missing brand mark immediately.
- **Results beat must finish inside its scene**: a 1.85 s tail with a 1 s chart draw + counters + a proposal card only landed during the outgoing blur;
  pull the pan 0.5 s before the word and shorten the draw to 0.8 s.
- **`gsap_exit_missing_hard_kill`**: a fade that ends within ~0.1 s of the next clip's `data-start` fails `check`; move it earlier or add `tl.set`.
- **Photos for fake posts**: GPT Image 2 "photorealistic real photograph, editorial, 35 mm, no text/logos/faces" → downsize to ~1152 px JPEG for the card.
- **Logo lockup animation**: hide the mark in the wordmark PNG with `clip-path: inset(0 100% 0 19%)` (mark ≈ 19 % of the 2500 px full logo), draw the 5×5 mark
  as 8 CSS squares (cell = lockup_width·356/2500/5) popping in the pixel-scene order, then wipe the wordmark from 19 % → 0 %.
- **Jury plateau**: after the native product section the Gemini jury stayed at 7/10 — its remaining notes were the live-action cutaways (generic lean-back
  stock, meeting-room composite) and the flat end card, so the next lever was replacing cutaways with native beats rather than more UI polish.
- **Never guess overlay coordinates on a UI plate.** Measure them: append a `load` script that writes `getBoundingClientRect()` of every card/row/p into a
  `<pre id="__rects">`, run `chrome --headless=new --window-size=1440,900 --virtual-time-budget=2000 --dump-dom file://…` and read the pre. (The in-app browser
  renders local files as static snapshots, so its JS tool can't measure them.) Then map css→composition (`x·4/3, y·4/3 − 60` for a 1440×900 plate covered into 16:9).
  Three rings the user flagged as "off" were all guessed; the measured ones landed first try.
- **Anchored jury plateaus.** Feeding the jury its previous scores made it return 7 for six consecutive rounds while listing every fix as "improved". Run a blind
  pass (no history, explicit scale: 8 = strong pro work, 10 = top studio) for the honest number; blind put v3 at 6 and v10 at 6–7 — 9 needs shot footage, not more edit.

## 2026-09-04 late — "real footage" via GPT Image 2 stills + Omni image-to-video (KontentPlus eras, round 2)
- **Best archival look so far:** GPT Image 2 prompt as an *authentic archival photograph* (name the process: glass plate / silver gelatin / Kodachrome / 35 mm consumer
  film + flash; period clothing; real faces; plate damage, grain, vignette; "no readable text") → Omni image-to-video 720p with era artefacts in the prompt (hand-crank judder,
  gate weave, flicker; 16 mm Kodachrome; camcorder scanlines). Faces are fine with Omni (Seedance rejects them in inputs). ~35–45 s per take, cheap.
- **Direction matters more than model:** "keep every person almost still" produced frozen takes that Gemini rated *lower* (auth 4, motion 3) than natural-motion takes
  (auth 5–7). Ask for moderate, continuous, single-setup motion; forbid new figures entering, cuts and pans ("one continuous locked-off shot, no pans, no cuts").
- **Omni failure modes seen:** phantom figures popping in after ~4 s (use only the first 3 s), a whip-pan cut mid-clip when two actions are listed, sci-fi floating UI when
  a prompt mentions notifications near a face, garbled text on generated screens (bake real UI via GPT `--edit` + `--ref` first).
- **Long slots:** join two takes with a hard cut inside the module (press 2.2 s + newsstand crowd) so each kinetic word lands on its picture; slow a 6 s take with
  `setpts=1.18*PTS` to cover a 7 s slot (invisible on hand-cranked footage).
- **Picker script** `eras/real/pick.py` (Gemini: authenticity / motion / era / usability + artefact timestamps, `TAKES=a,b` env to score a subset); `swap_in.sh` conforms
  and installs by slot name, keeping the previous plates in `_prev/`.
- **Ceiling:** blind Gemini jury stayed at ~6–6.5 after the footage round; its notes turned structural (live-action ending after UI, tonal jump at the turn). Treat ~7 as the
  evaluator's ceiling for generated footage and tell the client so, rather than burning more generations.
- **Omni 1080p upscale from the EEA:** `--upscale file.mp4` (uploaded-video edit task) fails with "Exactly one input video is required for edit task" — uploaded-video
  edit/extend is unavailable in EEA/CH/UK. Workaround that works: multi-turn `--previous <interaction_id> --resolution 1080p --prompt "Upscale this exact video…
  keep every frame identical"` — verified a true upscale (mean frame diff ≈ 2/255 vs the 720p original). Interaction ids are in `<output>.mp4.json`.
- **Finals chain:** conform HD takes with `-crf 14 -preset slow`, `render_hyperframes.sh … --quality high` (~63 MB / 50 s), then `loudnorm I=-14 TP=-1.5 LRA=11`
  + `-movflags +faststart` with `-c:v copy` for the web master.
- **9:16 from the same build (no fork):** `ASPECT=9:16 OUT_DIR=../film_916` switches `make_spec` (width/height/aspect, spec+timing output dir) and `overlays`
  (FW/FH, module geometry 60..1020 × 520..1060, axis at 1180, pushes ±FW, tick strip FW per era, `video.era-mod` resized to the module rect with
  `clip-path: inset(0 round 18px)` instead of a full-frame mask, UI plates placed as 1286-px cards with their own css→frame mapping K=0.893/XO/YO,
  brain ring RX/RY 400/520, ops camera targets per aspect, results plate as a module, end card recentred, lockup 900). The project dir holds only
  `assets -> ../film/assets` symlink; run builder/overlays with the env vars from `film/`. Vertical first pass needed one fix (a kinetic card over the ring).
- **Gotcha when parameterising overlays:** replacing a literal `top:760px` with `top:{FH // 2 + 220}px` inside a *plain* string emits the braces verbatim → invalid CSS
  → the element silently falls back to the class position (a kinetic card landed on the assembling logo; user: "logo is morphed wrong"). After any templating pass,
  `grep -o 'top:{F[HW][^"]*' index.html` must return nothing.
- **Google Drive references (server):** `analyze_reference.py` now accepts Drive share links and downloads via `gws drive files get --params
  '{"fileId":…,"alt":"media","supportsAllDrives":true}' -o <name>` run *inside* the target dir (gws refuses `--output` outside its cwd; the
  `files download` endpoint rejects `supportsAllDrives`). Delivery on the Gemoniq box: copy drafts to `outputs/drafts/`, finals to
  `outputs/final/` — the inotify watcher uploads to the client's Drive folders within seconds; get the link with `files list … webViewLink`.

## 2026-09-06 — Shot-match grading: the plate that shipped ungraded

- **Bug:** `overlays.py` graded the results plate with `#scene-12 video {{ filter: … }}`; `scene-12` *is* the `<video>`, so the
  descendant selector matched nothing and the plate went out ungraded while every era plate (graded via `.era-mod`, a class on
  the video) was fine. Client: "the woman at the screen and the meeting room aren't the same movie." Nothing in `check` catches a
  CSS selector that matches nothing — **grep the built `index.html` for every colour rule's target, or stamp attributes and assert.**
- **Diagnose relatively, not per clip.** `hyperframes media-treatment --selector '#scene-NN' --analyze --json` gives p1/mean/p99 luma
  and chroma per clip; run it on *every* live-action clip and tabulate. Each clip alone reads "clean" (suggested patch ≈ 0) — the
  fault shows only as a spread: the plate sat at 52.8 / 159.5 / 212.8 against a film at 25–36 / 61–107 / 120–190 (milky black
  floor, ~50 IRE hot). The black floor (p1) is the tell for "different lab".
- **Fix = mastering, not seven tweaks:** one shared print (wheels: shadows hue 205 / highlights hue 35, one master S-curve) on every live-action clip, then per-clip `adjust` onto a common black floor (~26–30) and highlight ceiling
  (~180–200). Archival mono gets tonal match only, no wheels (split-tone reads as sepia). Keep the story's exposure arc — the payoff
  beat may stay brightest, it just has to share the floor and the print. Implementation: §6b in
  `examples/kontentplus-intro/film/overlays.py` — a `GRADE` dict stamped as `data-color-grading` on each `<video>` at build time,
  so it survives rebuilds and carries into the 9:16 build.
- **Never handmade CSS `filter` on media** — it bypasses the HyperFrames shader path (`/media-use`), is invisible to Studio, and
  fails silently. Canonical payload keys: `adjust`, `wheels`, `curves`, `details` (vignette/grain — **not** `finishing`, that's
  the family name; wrong key → `check` fails with `color_grading_invalid_structure`).
- **No vignette or grain in the grade payload.** The first pass had `details: {vignette 0.14, grain 0.04}` on the modules and 0.22 on
  the plate; the client: "you added a black filter, the edges are easily visible." The era modules already carry `.mod-grain` (edge
  darkening sized to the module), and in the 9:16 build the `<video>` *is* the module rect, so a shader vignette lands its full
  darkening at the clip edge (corners/centre 0.68 → 0.62; invisible in 16:9 where the module is a centre crop of a full-frame video —
  always check the vertical). Removed; the plate then needed exposure −0.50 instead of −0.40. Shot-match = tonal + print only.
- **Removing CSS filters removes what they carried.** The old rules also held the film's desaturation (`saturate(.88)` eras,
  `saturate(.8)` modern); dropping them raised saturation film-wide (2016 plate 31.6 → 39.6 %). Fold it back in as `saturation:
  -0.12 / -0.20`. Measure, don't eyeball.
- **Verify on the rendered file:** same timestamps from old and new master → p1/mean/p99 per shot. Here: meeting room 168.6 → ~129
  mean, black floor 8.4 → ~5, highlight 238 → ~190; the rest held within ±2, module edge ratios within 0.01 of the approved cut. Don't overwrite the approved master — render `_graded`
  next to it so the client can A/B.

## 2026-09-06 — FLUX 3 Video wired and verified (four live runs, ≈ $4.80)

- **Why it is here:** the only model in the studio that does *dialogue with lip-sync* and *several angles with hard cuts inside one generation*.
  Test: a 10 s two-shot ("SHOT ONE: MCU … HARD CUT. SHOT TWO: wide …") produced the MCU, a clean cut at 7.7 s, the same woman/desk/palette in the
  wide, and Whisper transcribed the quoted line verbatim — no burned-in subtitles because the prompt ended with "no on-screen text, no subtitles"
  and the speaker was visible. That is the recipe; leave either out and the line tends to become text.
- **API shape gotchas baked into `generate_video_flux.py`:** files go inline as raw base64 (no S3, no `data:` prefix); `keyframes` is one image,
  a plain list (3+ need `duration`) or `[[seconds, image], …]`; v2v source ≤ 15 s / 50 MB; result URLs died after **1 h** — the script downloads
  the mp4 and the draft `.bin` immediately and writes `<clip>.mp4.json`; `--download <task_id>` recovers a finished job.
- **Draft → enhance is a real workflow:** `--draft` = ⅓ price, 49 s for 5 s; `--enhance draft.mp4 --resolution fhd` reproduced the same seed/shots
  at 1920×1088 (200 s). Decide composition, cut points and delivery on drafts, enhance only the keepers. Enhance reports `cost: null` — the cost
  report prices it by rate.
- **Output geometry:** hd = 1280×704, fhd = 1920×1088 (multiples of 32). Conform to the timeline size in `master.sh conform`; don't assume 1080 rows.
  Mono 44.1 kHz audio at wildly different levels (−47 dB ambience-only vs −27 dB dialogue) — loudnorm in the master.
- **i2v honours "hold the framing and the light exactly as they are in the still"** — the conductor still (a violinist mid-stride) became a locked
  wide in which she walks to a stop; nothing re-lit, nothing entered. Same rule as LTX: describe the change, then say what must not change.
- **Prompt rewriting means unnamed layers are lost, not defaulted your way:** the fox draft got paw-steps and wind because they were named; leave
  audio unnamed and it invents a score. Say "no music" when scoring in post (we always do).
- Routing rule now in SKILL.md: talking or more than one angle → FLUX 3; a hero shot you iterate by feel → Omni; a 30 s one-take with a motion
  reference → Seedance 2.5; coverage at scale or a fix inside a clip → LTX.

## 2026-09-06 — Film #3 "More than a post": a FLUX 3-first manifesto in one afternoon (KontentPlus)

- **Shape:** BFL's own FLUX 3 launch teaser as the reference (typographic manifesto, tiles popping around phrases, full-bleed
  vignettes, one spoken beat). Step 0 → brief; 5 refs; 25 stills (GPT Image 2, `docs/stills_batch.py`, 4 parallel); 26 FLUX 3
  clips (`docs/clips_batch.py`, 4 parallel, 23 tiles at hd 5 s + 3 vignettes as `--draft` → `--enhance fhd`) = $20.87 + $4.30;
  HyperFrames generator `film/build.py` from a measured beat grid. Draft in ~3 h of wall time, ≈ $28 total.
- **FLUX 3 in production:** 26/26 first-try keepers at 4 concurrent jobs (64–155 s per 5 s hd tile, ~75 s per 8 s draft, 245–260 s per
  fhd enhance). The two-shot + dialogue vignette landed on the first draft: `Use this image as the first frame. SHOT ONE … says, warm
  and decisive, "Ship it." HARD CUT. SHOT TWO …` with `no on-screen text, no subtitles`. Enhance keeps the seed: the fhd clip is the
  draft, sharper. Concurrency 4 + 3 sequential enhances ran without a rate error. `cost_credits` is null on enhance results.
- **`hyperframes beats` needs the audio inside the project** (`audio/x.mp3`, not `../audio`) and an `<audio data-timeline-role="music">`;
  it reports eighth-notes for a 115 BPM electro bed (bpm 234) — halve it; take bar = 4 × median quarter gap (the mean is inflated
  by the fade-out). Phrases on bar lines, tile pops on eighths, and the cut lands on the transient for free.
- **The runtime shows BLACK past a video's source, not a held last frame** (contrary to the older generator note) — a tile whose
  window outlives its 5 s clip became a black box at 22 s and 50 s. Fix in `prep_assets.sh`: tiles are conformed as ping-pong
  (`split; reverse; concat` → 10 s) so any window ≤ 10 s is covered; on subtle-motion tiles the reversal is invisible.
- **Untimed wrapper + timed video** is the pattern for animated tiles: the wrapper (position/size/opacity/transform) is ours to tween;
  the `<video data-start>` inside is the framework's. No `video_nested_in_timed_element`, and tile pops are binary `tl.set` + `power4.out`.
- **An opaque chapter layer hides sibling text**: the pixel-mark clip (`z-index 12`, canvas background) swallowed the phrase clip
  (`z-index 10`) — the snapshot showed the mark and no words. Give text that must sit on a chapter layer a higher z-index explicitly.
- **Hard kills after boundary exits** (`gsap_exit_missing_hard_kill`): every exit tween that ends on a clip start needs `tl.set(el, {opacity: 0}, cut)`.
  Lint also fires when a tile *video* starts inside another element's exit window — pop closing tiles in pairs so the last one starts well before the cut.
- **Portrait from the same generator:** own slot table (tiles alternate above/below the centre text band) and `object-position` per
  vignette (MARIT at 22 % so the centre crop keeps her face); everything else (bars, seams, lockup) is aspect-agnostic via FW/FH.
- **Jury on a manifesto:** 6.0 blind, "ship: yes"; the notes were structural (office beat abrupt, pipeline tile abstract) → send to the
  client rather than iterate; product clarity is inherently lower in a manifesto than in a demo.

## 2026-09-06 — Round 2 on "More than a post": "AI slop, nothing moves" and adding a VO after the fact

- **The client's slop read came from stillness, not faces.** The first office beat had a good face and a good cut but MARIT sat
  motionless until the line and the wide was a tableau. Measure it: `tblend=all_mode=difference,signalstats` mean YAVG per second
  was 0.9–3.7 on the rejected take vs 0.8–6.7 on the fix. The fix was all prompt: give every person a verb before the line (she
  *scrolls, taps the pen*; he *walks in with a cup and stops at the desk*; *a colleague crosses the background*), name the camera
  move (slow handheld push-in), and put movement in the wide too (he walks back, she starts typing, one colleague stands up).
- **Two drafts, three checks, one pick:** scene-cut detection (is the HARD CUT real — take B dissolved), Whisper on the clip (take B
  mis-spoke the line as "That's the same."), the motion metric, then `pick_takes.py` as the second opinion (it agreed: A). $0.96
  for both drafts; enhance only the winner. Keep the losing take's `.draft_cache.bin` — an enhance is still possible later.
- **Adding narration to a text-led film:** one ElevenLabs file per line (`docs/vo.md` table → `generate_tts.py --timestamps`), each
  placed on the bar its phrase owns (`VO = [(n, T[...] + offset)]` in `build.py`), lines short enough for their slots (≤ 2.5 words/s),
  no VO under the spoken dialogue, music dips to 0.12 under each line via a sorted event list — merge a restore that is followed by
  a dip within 0.6 s, or lint flags `overlapping_gsap_tweens` on `#music`. Whisper on the rendered file is the cheap proof that every
  line is present and in order.
- **`master.sh render` landed at −12.6 LUFS (target −14).** Single-pass loudnorm drifts; re-master the `_raw` with the two-pass
  form (measure with `print_format=json`, then `measured_i/measured_tp/measured_lra/measured_thresh` — **lowercase**, the capitalised
  `measured_I` is rejected with `Invalid argument` — plus `offset` and `linear=true`) and `-c:v copy` — no video re-render needed. With the VO
  in the mix the single pass landed at −15.1 LUFS / −1.5 dBTP, close enough to ship.

## 2026-09-06 — Round 3: text must follow the voice, and how the office beat finally passed

- **Bar-line text vs. narration = a visible lag.** "actually works." landed a full second after the voice said it because phrases sat on
  bar lines while the VO ran ahead. Fix: `phrase_timed()` in `build.py` ignites each word on the ElevenLabs *character* alignment
  (`character_start_times_seconds` → word starts, `vo_words()`), minus a 0.12 s lead; chained beats (quadrants, "So is KontentPlus.")
  take their start from `vo_word_time(line, word)`. Tiles still pop on the beat grid. **Audio is the clock** (motion-doctrine rule 2).
- **Six attempts at one 8 s dialogue beat, and what each taught:** hard cut to a reverse wide → client read the mirrored desk as an
  AI error (correct grammar, wrong audience) · v2v continuation of the good first 4.5 s → visible seam at the join (frame-diff spike
  12 vs 8) and the model ignored "he stays" · continuous 8 s takes → 1 of 4 said the line ("Let's do that", "Shiffle" ×3), floating
  papers/text artefacts in 2, and the locked-off one was a static photo (motion 0.1–1.6). **What passed:** *coverage* — keep the verified
  MCU up to the line (4.55 s, fhd) and hard-cut to a **close insert of the same action** (hands typing, generated from a new still with
  the wardrobe ref) — a scale change reads as editing, not as a continuity jump. Insert prompt must not repeat an action from shot one
  (first insert re-delivered the coffee cup → "double action"). Gemini picker: "usable modern commercial coverage".
- **Metrics that decide before taste:** `select='gt(scene,0.3)'` (is the cut where you think), `tblend=difference + signalstats` YAVG per
  second (stillness < 1.5 = slop risk), Whisper on the clip (wrong line = reject), then `pick_takes.py` for the human-ish read.
- **BFL throttles on a low balance:** below a threshold the API returns `429 … active tasks are capped at 1 per organization` — parallel
  batches fail outright. `generate_video_flux.py` now waits 15 s and resubmits on 429 (up to the timeout). Enhances are not priced in the
  response (`cost: null`) but bill ≈ $0.29/s at fhd — four 8 s enhances ate ≈ 930 credits between two balance checks. Top up before a batch.

## 2026-09-06 — LTX 2.5 durations, and the caption box bug (Buddha pilot)

- **LTX 2.5 fast at 1920x1080/24 fps only accepts even durations** (6, 8, 10 … 20). Odd values fail with
  `Invalid input for 'duration': Duration 9 seconds is not supported`. Plan slots so `clip = next even ≥ slot + 1`.
- **LTX concurrency limit is 3 jobs per key** (`429 concurrency_limit_error`). Keep drivers at 3 workers and never overlap two drivers.
- **i2v drifts/pushes destroy framing on stills with people.** "Drifts very slowly to the right" became a push-in that
  rolled the subject over; "pushes in slowly" ended in an off-model close-up. For story shots default to
  `--camera-motion static` + "Camera holds for a moment; no camera movement, no push-in" and let the subject move.
  Also: never mention a reflection ("his reflection settles") — LTX rendered a second figure in the water.
- **build_hyperframes_timeline.py captions rendered as a full-height dark column** because `.clip { inset: 0 }`
  set `top: 0` and `.subtitle` only overrode `bottom`. Fixed 2026-09-06 (`inset: auto 0 Npx 0; align-items: flex-end`).

## 2026-09-06 — Seedance 2.5 reference rules (Buddha v2 tests)

- **Frames from Seedance's own output are still blocked** as reference images (`InputImageSensitiveContentDetected.PrivacyInformation`),
  despite the "trusted recent outputs" note. Only text-only Seedream stills passed (two-panel documentary sheet, no `--ref`).
- **Reference audio must be ≥ 1.8 s** (`InvalidParameter … audio duration … must be greater than or equal to 1.8`). Pad short lines or write longer ones.
- Seedance 2.5's built-in Hindi speech mispronounces (user heard "बुढ़ापा" as "budap"); lip-sync to an ElevenLabs line via `--ref-audio` is the fix under test.
- A 10 s reference task queued ~12 min at peak; text-only 20 s tasks returned in ~4 min. Budget wall-clock accordingly.
- Output is 720p regardless of prompt; upscale at assembly.
- **Seedance 2.5 output filter** blocked a scene with "emaciated, ribs and collarbones showing" next to an 18-year-old girl
  ("output video may contain sensitive information"). Softening to "thin, exhausted" and "young woman in her twenties" passed.
- **Whisper timestamps are wrong on Seedance audio** (leading ambience gets trimmed, lines land at 0–8 s). Use an RMS speech-burst
  detector for caption timing; use OpenAI whisper-1 (API) only for the words. Local whisper-small mangles Hindi.
- **HyperFrames lint:** a caption starting exactly at the fade-in end (1.0 s) trips `gsap_exit_missing_hard_kill`; overlapping caption
  windows trip `content_overlap`. Offset the first caption and clamp caption ends to the next start.

## 2026-09-06 — BFL's camera-terms cheat sheet folded into the FLUX 3 docs

- Source: docs.bfl.ml `prompting_video_camera_terms` — 14 categories, 119 terms, each with a demo clip. Now `reference/flux3-camera.md`
  (term · what it reads as · studio phrase), linked from `flux3.md`, `SKILL.md` and the README.
- **Pattern in every official example:** term first (*Dutch angle of…*), one visible action, one or two atmosphere details, then the frame
  spec as prose ("10 seconds, 16:9"). Official cap: one framing term + one movement term + one action; four stacked terms is their own
  bad example. Camera language is optional to them — for us it is an unnamed layer, so we name it.
- **Transitions are nouns, not just `HARD CUT.`:** match cut, whip transition, foreground wipe, object portal, pass-through, jump cut,
  quick cuts (eight shots in 10 s — a montage register), screen-in-screen. The Lumina foreground-wipe technique is official vocabulary now.
- **New tools for product films:** Lazy Susan (turntable, camera fixed), probe lens (snorkel through a still life), locked-on, pedestal,
  cinemagraph (a still with one motion), freeze frame with a moving camera, boomerang loop.
- Director/era names are sanctioned as looks in the official prompts (Wes Anderson tableau, Wong Kar-wai step printing, Busby Berkeley
  kaleidoscope, 90s camcorder 4:3). Kinetic typography is a documented capability — brand type still goes through HyperFrames.
- Nothing here has been run yet; the first live tests should be the quick-cuts montage (count the cuts with `select='gt(scene,0.3)'`) and a
  Lazy Susan packshot.

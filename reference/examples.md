# Worked prompt examples by model — curated from official guides and production write-ups

> Collected 2026-09-05. Verbatim where marked with quotes; each block names its source. Use these as *shapes* to copy,
> then fill with the lock blocks from Step 1. Our own project write-up lives in `../examples/kontentplus-intro/`.

## The shape every model agrees on

| Slot | Omni (Google) | Veo 3.1 (Google) | Seedance 2.5 (ByteDance) | LTX-2.5 (Lightricks) |
|---|---|---|---|---|
| Order | scene → camera → light/mood → audio → negatives | **[Cinematography] + [Subject] + [Action] + [Context] + [Style & ambiance]** | subject+event → setting → visual treatment → camera → sound → timeline → continuity | one present-tense paragraph: shot, scene, action, character, camera, **audio** |
| Timing | `[0-3s] … [3-6s] …` or "After 3 seconds, …" | `[00:00-00:02] …` blocks with SFX per block | `[0-8s] initial state. event. camera. end state. [8-17s] continue invariants …` | 2–3 shots max per clip; name the cut, re-establish shot, re-name characters, state sound at the cut |
| Audio | say it explicitly: "No dialogue", "single low cello note building" | `A woman says, "…"` · `SFX: …` · `Ambient noise: …` | markers: `{dialogue}` `<effects>` `(music)` `【subtitles】`; "No subtitles" | rank 1 — "anything left out gets invented"; attach every sound to something visible; "no music" when you score in post |
| Edits | "Change X. Keep everything else identical." · `--previous` | first/last frame + refs ("Using the provided images for …") | "Edit @Video 1 only from [t] to [t]. Change […]. Keep […] unchanged." | end-frame image made by *editing* the start frame (avoids drift) |
| Text on screen | can render words ("One word on the screen at a time: …") but we still composite in HyperFrames | avoid | "exact signs, subtitles, packaging copy … belong in post" | "compose in post" |
| Negatives | "No dialogue. No embellishments. No extra sound effects." | describe the *scene without* it ("a desolate landscape with no buildings or roads") | closing hard-constraint list (see UGC template) | drop mood words; give physical cues instead |

---

## Gemini Omni 1.1 Flash — official examples (ai.google.dev/gemini-api/docs/omni)

- Text-to-video: "A marble rolling fast on a chain reaction style track, continuous smooth shot." · "A drone shot of a mountain landscape at sunrise."
- Image-to-video from a sketch: "turn this into realistic footage, using the drawing only as a guide for movement, do not show the drawing in the final video"
- First→last frame: "A smooth cinematic transition from a lush green forest at sunrise to a snowy forest under a starry night sky."
- Subject reference: "A cat playfully batting at a ball of yarn." (with `<IMAGE_REF_0>`)
- Edit (multi-turn, `--previous`): "Make the violin invisible." · "Change the jacket to bright yellow." · "Put a fashionable hat on this person" — always append **"Keep everything else the same."**
- Extend: "Continue the scene." · "Extend this video: have the character shown in <IMAGE_REF_0> enter the scene and wave."
- Timing: "After 3 seconds, a woman enters the scene." · "[0-3s] A person is walking [3-6s] They stop and turn around [6-10s] They start running"
- Text: "One word on the screen at a time: 'did, you, know, that, Omni, can, do, awesome, text?' Each word appears for 1s with a different animated style"
- Documentary still-life example (Google): "Continuous, unbroken handheld shot of a fluffy tabby cat sitting on a sunny windowsill … Sound design: Gentle breeze, distant bird chirps. No dialogue."
- Limits: ≤10 s per generation, extend +3–10 s to 40 s total, ≤3 reference videos of ≤3 s, 360p/720p native, 1080p/4K are upscales; uploaded-video edit/extend unavailable in EEA/CH/UK (use `--previous`; our script does this for `--upscale`); cannot add dialogue when extending an uploaded talking clip.
- Community-confirmed technique (promptslove): omit the camera and you get "medium shot, static"; name durations inside the prompt ("eight-second push in"); audio in physics words ("deep metallic thud"), instrumentation by name; list several edits as numbered items in one turn.

**Our additions from the KontentPlus film:** archival still → Omni with era artefacts in the prompt; ask for *moderate continuous* motion in *one* setup ("no one enters or leaves, no new figures, hands keep their shape, no pans, no cuts"); phantom figures appear after ~4 s; mentioning notifications near a face spawns floating UI; "no music" is sometimes ignored — mix in post anyway.

## Veo 3.1 — official examples (Google Cloud "Ultimate prompting guide for Veo 3.1")

- Formula example: "Medium shot, a tired corporate worker, rubbing his temples in exhaustion, in front of a bulky 1980s computer in a cluttered office late at night. The scene is lit by the harsh fluorescent overhead lights and the green glow of the monochrome monitor. Retro aesthetic, shot as if on 1980s color film, slightly grainy."
- Crane: "Crane shot starting low on a lone hiker and ascending high above, revealing they are standing on the edge of a colossal, mist-filled canyon at sunrise, epic fantasy style, awe-inspiring, soft morning light."
- Dialogue with references: "Using the provided images for the detective, the woman, and the office setting, create a medium shot of the detective behind his desk. He looks up at the woman and says in a weary voice, 'Of all the offices in this town, you had to walk into mine.'" → reverse: "… A slight, mysterious smile plays on her lips as she replies, 'You were highly recommended.'"
- First/last frame transition: "The camera performs a smooth 180-degree arc shot, starting with the front-facing view of the singer and circling around her to seamlessly end on the POV shot from behind her on stage. The singer sings 'when you look me in the eyes, I can see a million stars.'"
- Timestamped 8 s: `[00:00-00:02] Medium shot from behind a young female explorer … [00:02-00:04] Reverse shot … SFX: The rustle of dense leaves, distant exotic bird calls. [00:04-00:06] Tracking shot … Emotion: Wonder and reverence. [00:06-00:08] Wide, high-angle crane shot … SFX: A swelling, gentle orchestral score begins to play.`
- Audio grammar: `A woman says, "We have to leave now."` · `SFX: thunder cracks in the distance` · `Ambient noise: the quiet hum of a starship bridge`. Keep lines one breath long (clips are 4/6/8 s).
- Vocabulary lists: dolly, tracking, crane, aerial, slow pan, POV · wide, close-up, extreme close-up, low angle, two-shot · shallow DoF, wide-angle, soft focus, macro, deep focus.
- Negatives: describe the scene *without* the thing, not "no X".

## Seedance 2.5 — official prompt-guide patterns (ByteDance/Dreamina via melies.co) + API examples (awesome-seedance-2.5-api-prompts)

Core formula: "[Subject] performs [specific action] in [setting]. The image uses [light, texture, palette, and medium]. The camera uses [shot size, angle, movement, and cut behavior]. Audio contains [dialogue, ambience, effects, or music]."

Reference assignment (one job per upload — the single most important rule):
- "@Image 1 defines [identity or object feature] only. Ignore [unwanted content]."
- "@Image 1 shows the front… @Image 2 shows the left side… All three images define one [object]. Only one [object] appears in the video."
- Conflict hierarchy: character identity → essential prop geometry → wardrobe → location/layout → lighting/texture → motion/camera style.
- "@Image1 is the main character. @Audio1 is the background score. She walks through neon-lit Tokyo alley"

Multi-shot (30 s): "[0-8s] Initial state. Event. Camera. End state. [8-17s] Continue invariants. Event. Camera. End state." — one event + a visible hand-off per stage; timestamps allocate time, they are not frame-accurate.

Dialogue / lip-sync: "Nia speaks quietly, without turning toward camera: {I knew I had missed it.}" — name speaker, language, delivery; markers `{}` `<>` `()` `【】`; add "No subtitles" or the line becomes on-screen text.

Edit / extend: "Edit @Video 1 only from [time] to [time]. Change [specific element]. Keep [everything else] unchanged." · "Extend @Video 1 forward. First frame continues its last frame. Preserve [locked elements]. [Subject] continues toward [direction], exits, and [settling action]." · API examples: "Turn the sunny afternoon into a rainy blue-hour scene while preserving the subject and camera movement" · "Continue the camera move forward into the glowing city entrance"

Image-to-video: "The camera slowly pushes in as she turns to face us, hair blowing in the wind" · first/last: "Smooth cinematic transition, camera drifts forward as the scene morphs from day to night"

API facts: duration 4–30 s (`-1` auto), 480p–4K (1080p/4K upscaled from 720p), `camera_fixed`, `generate_audio` (edit/extend), `seed` keeps a neighbourhood not an identity, **first 20–30 words carry most weight**, early references weigh more, "one strong lighting keyword beats ten adjectives", target 60–100 words, `mov` for edit/extend chains, faces in *inputs* are rejected (Seedream 5 workaround in `seedance.md`).

Pitfall table (official): character drift → one identity ref, repeat the name, exclude background/pose · duplicate props → "all views define one object; only one appears" · random camera → one move with start and end frame · theatrical acting → 2–4 physical cues (gaze, breath, posture, hands) · rushed long clips → fewer beats or more time.

## LTX-2.5 — official guide shape (ltx.io / fal.ai / runware)

Six things in **one present-tense paragraph**, ranked: sound → camera → character detail (emotion as visible action) → shot & scene → action → dressing.

- Runware's pattern: "A wide shot easing into medium, late-afternoon sun through windows, modern living room with oak floors and plants, she walks in with a mug, crosses to window, stops to watch the city as light catches steam, woman in cream sweater, camera pushes gently from doorway and follows her, quiet footsteps on wood, faint city hum, no music."
- Audio line pattern: "The audio is soft and open: occasional deep whoosh of balloon burners, gentle high-altitude breeze, distant birdsong, no music."
- Dialogue: quote the line, note accent/delivery, and write "a beat of stillness before he speaks" (lip-sync clarity); "voice close and dry with room reverb, traffic, radiator ticking".
- Multi-shot (2–3 max): at every cut name the edit type (hard cut / dissolve / match cut), re-establish scale-angle-lens-light, re-name characters with their original descriptors (never pronouns), state what the sound does at the cut.
- Image-to-video: one event inside the still ("pouring spirit into a rocks glass, ice cracks"), protect the framing and light by naming them; start+end frames must share dimensions; make the end frame by *editing* the start frame.
- Audio-to-video: the track sets duration (2–20 s); name the visual element that lands on each accent (flamenco heel stamps).
- Settings: Pro 6/8/10 s or auto, 720/1080p, 24/25/50 fps; Fast 6–20 s, up to 4K. ~$0.12/s Pro 1080p.
- Avoid: mood adjectives, readable signage, a prose camera move *and* an enum camera setting, chaotic motion.

---

## Production shapes worth copying

### 30 s UGC product ad in one Seedance 2.5 generation (imastudio.com tutorial)

Six 5 s beats: hook/problem → product reveal → detail/usage setup → demonstration → result/feeling → product-and-face CTA hold. Prompt sections, in order: **REFERENCE ASSET ROLES** (@Image1 product geometry only · @Image2 face/hair/age/skin only · @Image3 environment+light only, "do not copy people or products" · @Video1 camera rhythm only · @Audio1 voice tone only) → **GLOBAL SCENE AND VISUAL STYLE** (one location, consistent light direction, smartphone look, subtle handheld) → **IDENTITY LOCK** (same person, product never changes size/shape/colour/label) → **TIMESTAMPED STORYBOARD** → **CAMERA RULES** ("only one primary camera movement per segment; all movements motivated by subject action; avoid random orbiting, whip pans, unexplained jumps") → **AUDIO DIRECTION** → **NEGATIVE AND HARD CONSTRAINTS** ("No identity drift. No product deformation… No extra hands, fingers, arms… No product passing through fingers… No text overlays, subtitles, watermarks") → **ENDING CONSTRAINTS** ("Hold final product-and-face composition steadily for final two seconds… No new motion, object, cut, or fade before video ends").
Lessons: separate constants from variables; beats matter more than description length; negatives must name *real* failure modes; lock the last 2–3 s for the end card; too much polish kills UGC believability.

### Cinematic car commercial, asset-lock method (higgsfield.ai breakdown, Seedance 2.0)

1. Build and lock every asset first: three-panel character sheets (rear, front, close-up), standalone car/prop sheets, screenshot the establishing shot as a location reference. 2. Attach the same assets by name to every scene prompt (`@image_1`). 3. Write scene prompts with a stated cut budget ("exactly seven shots and six cuts", "exactly three shots, only two cuts") and locked geography (who stands where, camera side). 4. Constants across the film: Kodak 500T grain, 16:9, SFX only. 5. Slow-motion inserts at named frame rates (120/240 fps). 6. Hard cuts, layered SFX in post. Lessons: reflections need explicit motion logic ("palm reflections drift vertically, not sideways"); rear-view-mirror framing gets eyelines without to-lens looks; screenshot single frames from static takes to mint new locked elements.

### Product-launch keynote choreography (chatcut.io production prompts, Seedance 2.0)

Named camera positions in sequence so the model follows a plan instead of averaging: extreme macro with grazing light → dolly push (mid to three-quarter) → 360° orbital → low-angle power shot from the floor → lateral tracking profile sweep → top-down descent with pull-back to the centred hero. Rules: one shot = one camera move; named nouns over adjectives ("volumetric overhead beam lighting", not "cinematic"); 4–6 s for logo reveals, 15 s for morphs; end every prompt with a defensive clause ("no cuts, no text overlay"); put duration and aspect in the opening clause.

### Ad structures (lumalabs.ai, 25 prompts) — the timing rules, model-agnostic

Hook inside 2–3 s on social, 5 s on skippable pre-roll; product reveal *after* a problem/context beat; CTA in the final 3 s; before/after = problem close-up → application → reveal; unboxing = overhead-to-eye-level arc; app demo = frustration → interface simplifies → ≤3 features; a "localisation template" keeps product, light and movement fixed and swaps setting, talent and text.

---

## Sources

- Google — Generate and edit videos with Gemini Omni Flash: https://ai.google.dev/gemini-api/docs/omni
- Google Cloud — Ultimate prompting guide for Veo 3.1: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- ByteDance/Dreamina Seedance 2.5 prompt guide (BytePlus ModelArk doc 2607689; patterns quoted via melies.co): https://docs.byteplus.com/en/docs/ModelArk/2607689 · https://melies.co/seedance-2-5-prompt-guide
- Seedance 2.5 API guide & prompts: https://github.com/Anil-matcha/awesome-seedance-2.5-api-prompts
- LTX-2.5 prompt guide: https://ltx.io/blog/ltx-2-5-prompt-guide · https://fal.ai/learn/tools/how-to-use-ltx-2-5 · https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/prompting
- Omni techniques (community): https://promptslove.com/blog/google-omni-prompting-guide/
- Seedance 2.5 UGC ad tutorial: https://imastudio.com/blog/seedance-2-5-prompt-tutorial-ugc-ad
- Cinematic car commercial breakdown: https://higgsfield.ai/blog/ai-car-commercial-youtube-guide
- Seedance 2.0 production prompts: https://chatcut.io/blog/seedance-2-0-prompts-examples
- 25 AI prompts for video ads: https://lumalabs.ai/news/ai-prompts-video-ads

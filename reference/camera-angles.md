# Camera angles — name the evidence, ban the cousin, check the tell (2026-09-27)

The studio's working copy for choosing, prompting and reviewing camera angles on every model (GPT Image stills, Omni,
FLUX 3, Seedance, LTX, Veo). Learned from reading the 19 *Camera Angles* entries of Melies' Cinematic Bible
(https://melies.co/cinematic-techniques) and cross-checked with the vendored DirectorSKILL
([cinematic-language.md](../vendor/DirectorSKILL/references/cinematic-language.md): height ladder, 180° and 30° rules).
The wording, cards and prompts here are ours. Melies is a reading reference only: do not paste or bulk-import its text
(its terms prohibit scraping). Moves, lenses and FLUX phrasing live in [flux3-camera.md](flux3-camera.md).

## The three ideas that matter

1. **An angle is five dials, not one word:** height · pitch · roll · facing · whose eyes. They are independent. A low
   camera that stays level is a *height* choice, not a low angle; a raised camera that stays level is a high *vantage*,
   not a high angle; a tilted horizon is roll, never pitch; three-quarter is facing, never tilt. Every dial you leave
   unnamed falls to the model's default.
2. **Every angle has a wrong cousin** — the neighbouring setup the model produces when the words are vague: high angle →
   drone top-down, low angle → worm's-eye, profile → three-quarter, POV → over-the-shoulder. Name the cousin in the
   prompt as a ban.
3. **Write the evidence, then check the same evidence.** Models honour what the frame should *show* (ceiling above his
   head, table edges parallel to the frame, far eye hidden, the trunk rim on three sides) far better than numbers or mood
   words. That same visible evidence is the *tell* you check in review. Degrees are a secondary hint (Dutch ~20°,
   incline ~8°, face turned ~45°), never the only instruction.

## The five dials

| Dial | Settings | Write it as visible evidence |
|---|---|---|
| **Height** — the lens against the *subject's* eyes | ground (a few cm) · hip/belt · shoulder (just under the eyes) · eye · above (step-stool → ladder → crane → far above) | what fills the near foreground: grit and boots (ground), hands and belt (hip); whose eyes the lens matches |
| **Pitch** — tilt up or down | level · down ~20–45° (high) · steep down from far above (bird's-eye) · straight down, close (overhead) · up (low) · almost straight up from the ground (worm's-eye) | ceiling/sky vs floor share; verticals converging up or down; where the horizon sits (low, high, gone) |
| **Roll** — rotation around the lens | level · ~5–12° (incline) · ~15–30° (Dutch) · past ~45° it reads as a mistake | horizon and door frames tilted left–right while the walls themselves stay straight |
| **Facing** — the subject's head against the lens | front (into the lens) · three-quarter (~45°) · profile (90°) · back | how many eyes and ears show; where the eyeline goes (lens, just off-lens, out of frame) |
| **Whose eyes** — who owns the view | objective (default) · POV · first-person · object POV · fourth wall · inside a container (trunk) | what sits at the frame edges (nothing, a hand, a fixed piece of an object, a rim); whether anyone looks into the lens |

Rules that come with the dials:

- **Relative, not absolute.** Height is measured against the subject's eyes: a seated subject needs a seated camera, and
  a standing camera on a seated person is already a high angle. In shot/reverse, set the lens at the *off-screen*
  character's eye height (cinematic-language.md).
- **Model defaults** for unnamed dials are usually: around eye height with a slight upward "poster" tilt on portraits,
  level roll, a three-quarter face, an objective viewer. Write eye level out in full — portraits drift low.
- **One angle per shot, on a budget.** Eye or shoulder level is the baseline and every departure is a story beat.
  Dutch and incline only read next to level shots (never cant every setup); bird's-eye and overhead about once per
  scene; worm's-eye rarely.
- **Refs pull the angle.** A front-facing character sheet tends to pull stills toward a front-on eye-level portrait.
  Give the ref one job (*"Image 1 is for the face only"*) and state the new camera position in full.

## Pick by story job

| The beat is… | Angle | Usually confused with |
|---|---|---|
| two equals; a face we should simply believe | eye level | shoulder level |
| walking beside someone | shoulder level | eye level, over-the-shoulder |
| the hands will decide | hip level | cowboy shot, low angle |
| the story starts from the floor | ground level | low angle, worm's-eye |
| someone small, watched or trapped | high angle | bird's-eye, overhead |
| people as pieces of a pattern | bird's-eye | high angle |
| a surface as a diagram (table, bed, formation) | overhead top-down | high angle |
| power, monument, threat | low angle | worm's-eye, low-but-level |
| the subject erases you (awe, terror) | worm's-eye | low angle |
| something is slightly off | incline | Dutch |
| the world is off its axis | Dutch | low angle, Dutch roll (a move) |
| the default narrative portrait | three-quarter | profile |
| withholding, secrecy, a statue | profile | three-quarter |
| answering a look | reverse angle | POV |
| being the character for one look | POV | over-the-shoulder |
| being the character's body for a stretch | first-person | POV, follow shot |
| the object sees | object POV | first-person, drone |
| the character lets us in | fourth wall | interview eyeline |
| we are the hidden thing in a container | trunk shot | low angle |

## The 19 cards

**Use it for** (and what it is not for) · **Write** (the evidence, *ban* in italics) · **Drift → tell** (what the model
usually makes instead, and how you see it in the frame).

### Height and pitch

| Angle | Use it for | Write | Drift → tell |
|---|---|---|---|
| Eye level | peers, honest dialogue; not for rank, surveillance or maps | camera at her eye height (seated if she sits), horizon level, no ceiling in frame; *no upward or downward tilt* | a mild low "poster" angle → ceiling visible, underside of the chin, verticals leaning in |
| Shoulder level | a companion walking beside the subject; not a formal portrait, not an OTS | camera at his shoulder, just under his eye line, a pace to the side as he walks, horizon almost level; *no foreground shoulder* | formal eye level, a low power tilt, or an OTS → pupils level with the lens / ceiling / a blurred shoulder in frame |
| Hip level | standoffs, a pocketed weapon, a key passed at the waist; not when the face is the whole event | camera at belt height and level, looking between the two figures, hands and belts sharp, faces in the top third | a power tilt, or a cowboy crop from eye height → nostrils and ceiling / a mid-thigh crop seen from above the chest |
| Ground level | the story starts at the floor: boots, tyres, an arrival, a dropped object; not a walking conversation | lens a few centimetres above the ground, wet cobbles or gravel sharp in the foreground, horizon very low | a kneeling-height low angle → clean floor with no near texture (only sky and nostrils = it went worm's-eye) |
| High angle | someone small, watched or trapped; a readable map of a room; not a power beat, not a plan view | camera above her looking down ~30°, more floor than wall, face still readable, walls in perspective; *not top-down, no drone move* | a drone plan → crowns of heads, the table a perfect rectangle; or a raised camera kept level → no downward tilt at all |
| Bird's-eye | crowds, courtyards, rituals as a pattern seen from great height; not faces or lines | from far above looking almost straight down, people as small shapes, the floor as a map; *locked, no drone flight*; seated groups: *no extra arms* | a step-stool high angle with a readable portrait, or a close product flat-lay with no sense of drop |
| Overhead top-down | a surface as a diagram: table, bed, desk, crime scene, formation; not a line on a face | straight down at 90°, table edges parallel to the frame edges, no wall or horizon, shadows falling across the surface; name the surface and its size | a steep high angle → a trapezoid table, a wall, eyes looking up at the lens; or the wrong scale (a street instead of a table) |
| Low angle | power, monument, threat: a figure filling the doorway; not peers, not every hero | camera below his eye line tilted up, ceiling beams or sky above his head, door frames leaning in toward the top, face still a portrait; *not from the ground* | worm's-eye or boots → only nostrils and sky; or low but level → door frames stay perfectly vertical |
| Worm's-eye | the subject erases you: a hull, a tower, a giant; not a power two-shot | lens on the ground pointing almost straight up, verticals rushing to a point above the frame, no horizon | stops at a waist-high low angle → a full readable portrait, a horizon, no convergence |

### Roll

| Angle | Use it for | Write | Drift → tell |
|---|---|---|---|
| Incline | a whisper of unease, a corridor that feels slightly wrong; not a real slope | horizon tilted only slightly (~8°), almost level, walls straight, static | a full Dutch → a diagonal horizon you could hang a picture on |
| Dutch | the world off its axis: a bent mind, an unfair fight; not decoration on every villain | static, horizon tilted ~20°, walls straight, natural body proportions; *the camera does not rotate*; neighbouring shots stay level | pitch instead of roll (ceiling visible, horizon level), a rotating camera (that is the *Dutch roll* move), or a 60° cartoon lean |

### Facing and the axis

| Angle | Use it for | Write | Drift → tell |
|---|---|---|---|
| Three-quarter | the default narrative portrait: a face with volume that still belongs to the scene | face turned ~45° from the lens, both eyes visible, one ear, eyeline to a partner out of frame; state the height separately | profile (far eye gone) or a passport front (both ears equal) |
| Profile | withholding, secrecy, a statue; not a scene where we must read a lie | exact side view, far eye hidden, the nose breaking the cheek line, looking out of frame with space ahead of the face; a living head, not a cut-out | slides back to three-quarter → the far iris shows |
| Reverse angle | answering a look in dialogue or a standoff | the opposite end of the same axis, same shot size as shot A, the lens at the off-screen character's eye height (equals get matched heights; a standing and a seated character look down and up at each other), eyelines opposed: A looks screen-right, B screen-left | crosses the line or changes size → both faces look the same way; a wide answering a close-up |

### Whose eyes

| Angle | Use it for | Write | Drift → tell |
|---|---|---|---|
| POV | forcing identification for one look | what he sees, at his eye height, no part of him in frame (no shoulder, no back of the head); cut it as look → POV → reaction | an OTS, or the looker facing the lens → a shoulder, the back of a head, eyes on camera |
| First-person | the audience *is* the body for a stretch: running, climbing, searching | his own hands or tools enter from the frame edges, the camera moves with his walk and head turns, his face never seen (except in a reflection) | a clean POV plate (no hands) or a follow shot from behind → no body at all, or the back of a head |
| Object POV | the prop has eyes: phone, bottle, bike, bullet, product | camera rigidly mounted on the named object, a piece of it fixed at one frame edge, the world moving around it | first-person hands or a free-flying camera → fingers and breath, the anchor edge drifting |
| Fourth wall | the character lets the audience in: a confession, a dare, a plan explained to us | looks straight into the lens, both pupils on camera, eye level; the others in the room do not look | an interview eyeline → eyes just past the lens |
| Trunk shot | we are the hidden thing: someone opens a container and looks in | from inside the car boot or box looking up, the dark rim framing several sides, faces leaning over the opening looking down into the lens; *the camera stays inside* | a generic low angle in a car park → no rim, full standing bodies, the camera rising out |

## Product and ad uses

- Overhead top-down = flat-lays, ingredients, an unboxing on a table (name the surface and its size).
- Low angle from counter height = the product as a monument; worm's-eye = a sneaker stepping over the lens.
- Object POV = the product's view of the user (from inside the fridge, the phone looking up at a face, a bottle on a bar).
- Trunk shot = from inside the box as the lid opens: the unboxing seen by the product.
- Three-quarter at eye level is the honest packshot; profile for a silhouette reveal.

## Light follows height

- Overhead and bird's-eye: top light flattens everything; use a raking key so shadows draw across the surface.
- High angle: the camera is up among the hanging lamps; they become the key and top light shapes the face.
- Low angle: the ceiling or sky is now in frame and must be designed (beams, practicals, clouds), not left blank.
- Ground level: backlight the grit, wet or dust so the near field reads.
- Profile: an edge or rim light separates the nose and brow from the background.
- Trunk shot: a bright opening and a dark interior; the key comes through the lid.

## Stills and video

- **The still owns the angle.** Get height, tilt, roll and facing right in the GPT Image still and check the tell there
  (cents), not in the clip (dollars). In image-to-video the video prompt names only the move and adds *"keep this camera
  height and angle"*; naming a different angle invites the model to move the camera to reach it.
- **Elevated views grow wings.** High, bird's-eye and overhead clips tend to become drone flights; write *"locked
  elevated camera, no drone move, no zoom"* unless you want the move (*crane over* is the move that arrives at a
  bird's-eye).
- **Dutch in video:** *"static cant, the camera does not rotate"* — otherwise you get a Dutch roll.
- **POV and first-person motion:** only the motion a body makes (walk rhythm, head turns), no shaky-cam effect, no
  owner face.
- **Multi-shot** (FLUX 3 `SHOT N:`, Seedance time-coded beats): restate every dial at each cut; a reverse keeps the
  shot size and puts the lens at the off-screen character's eyes; consecutive shots of the same subject change angle by 30° or more (cinematic-language.md, 30° rule).
- **Lenses:** eye level 35–50 mm; three-quarter and profile 50–85 mm; first-person 24–35 mm; wider glass exaggerates
  the convergence of low and worm's-eye angles; a fisheye hides an incline.

## Review: check the tell

Run this on every storyboard still and every clip (SKILL.md Steps 3–4). If you see the cousin, retake with its ban line
added — a prompt edit is the cheapest rung of the cost ladder.

1. **Horizon:** level, tilted (roll), or gone (overhead, worm's-eye)?
2. **Verticals:** parallel (level pitch), converging toward the top (looking up) or toward the bottom (looking down)?
3. **Ceiling vs floor:** which one takes the frame?
4. **Eyes:** how many show, and where do they look (lens, just off-lens, out of frame)?
5. **Frame edges:** a shoulder, hands, a fixed piece of an object, a rim, or nothing?
6. **Near foreground:** ground texture, hands and belts, or clean air?

## In the shot list (G3)

Write the angle column as dials — `height · pitch [· roll] [· facing] [· whose eyes]` — for example
`seated eye · level · 3/4 left`, `above · down 30°`, `belt · level`, `ground · up steep`, `eye · level · roll 20°`,
`POV Ravi · eye · level`. The director's sheet prints it under each shot (`shots[].angle` in `plan.json`), so the
reviewer approves angles before anything renders.

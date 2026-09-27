# Directing — story before pixels, and how to keep a take honest

Why this file exists: the Buddha pilot (2026-09-06) rendered two full 2-minute cuts before anyone could say why the
hero sits under the tree or why a girl brings him kheer. The footage was fine; the story was never locked. The three
vendored skills in `vendor/` (see `vendor/VENDOR.md`) each solve a piece of that. This is the distilled, mandatory
version for ai-film-studio. It sits **in front of** Step 1 of `SKILL.md`.

Credits: gated development after Yuval Avidani's *director* skill; scene formula, three-detail rule, three-jobs rule
and Murch's Rule of Six after Serge Shima's *visual-skills* (CC BY 4.0, https://github.com/smixs/visual-skills);
identity string, continuity axes and the failure ladder after wangzhang-wu's *DirectorSKILL* (MIT).

---

## 0. The four gates (words are free; renders are not)

Run in order. Each gate is a full stop: present, get an explicit yes, then move. Nothing visual is generated before
Gate 1, and no video before Gate 3. If the user says "just generate something", say in one sentence why not yet and
keep developing. (For a trivial 15-second product loop, Phases 1–2 can be light; Gate 1 still happens.)

| Phase | Deliverable | Gate |
|---|---|---|
| **0 Intake** | Kill shot (the ONE thing the viewer should feel/do at the end) · exact duration · platform + aspect · subject · audience · language · existing assets · recurring characters · hard constraints | G0: reflect the brief back in 5 lines |
| **1 Concept** | 2–3 concepts, ≤120 words each: logline · dramatic question · want vs need · the one visible demo · emotional arc · style + why · open wound. Run the tests below and report verdicts | **G1 (hard): lock ONE concept in words** |
| **2 Beats** | Timed beat sheet: `t-start–t-end · what happens · value shift (+/−) · setup/payoff carried · what the audience learns` → rendered as the **director's sheet** (`scripts/director_sheet.py`, one page, previs per scene, approve / needs-changes per scene) | G2: approve structure on the sheet |
| **3 Shots** | Per shot: size · angle as dials (height · pitch · roll · facing · whose eyes — [camera-angles.md](camera-angles.md)) + movement (with its reason) · lens/DOF/light · sound cue · transition in · which beat it serves. Identity strings written **here**, not later | G3: approve the shot list — last cheap stop |
| **4 Production** | Stills → takes → audio, per `SKILL.md` Steps 2–5 | G4: approve per shot; re-roll here, not in the edit |
| **5 Post** | Audio spine first, assemble to the beat sheet, hide seams, mix, one grade pass, deliver | — |

### Concept tests (say the verdicts out loud)
- **Spine**: one sentence with a want and an obstacle? *Once upon a time… every day… one day… because of that… because of that… until finally…*
- **But/therefore**: do the beats chain with "but" and "therefore", never "and then"? A list is not a story.
- **Wound / stakes / turn**: if it feels thin, one of these is missing. Check them first.
- **Single demo**: exactly one visible thing happening, with a result?
- **Hook contract**: what do the first 3 s promise, and does the ending keep it?
- **Scope axe**: is there a second film hiding in here? Name it, cut it.
- **Ending first**: know the last image before writing the middle.
- **Discount the first five ideas**: the obvious version is the AI-slop version.

### The audience-knowledge ledger (the Buddha failure)
Every fact the ending depends on must be *planted on screen* in an earlier beat, by an action or a line a character
would actually say. Keep a two-column ledger — `fact the audience needs` → `beat where they get it` — and refuse
Gate 2 while a row is empty. "Why does he sit under the tree" and "why does she bring the kheer" were empty rows.

---

## 1. A scene exists only when all five are present
```
Scene = desire + obstacle + space geometry + controlled gaze + editing rhythm
```
Name each in one sentence before writing a prompt. **Desire**: what the character wants this second. **Obstacle**:
what blocks it. **Geometry**: who stands where, who holds the power position, which way is threat and which is exit.
**Gaze**: the one thing the viewer's eye is forced to. **Rhythm**: how long each shot lives and where the cut bites.

**Three jobs.** Every shot must change emotion, advance action, or increase pressure. A beautiful establishing shot
with none of these is wallpaper — delete it.

**Three details per shot.** One environmental pressure (cold tube light, rain on one pane, a tight corridor), one
physical micro-action (jaw locks, knuckles whiten, eyes drop a quarter inch), one sound or visual motif anchor tied
to the spine. Emotions are never *named* in a prompt ("he is sad"); they are rendered by the body.

**Banned words** in prompts: cinematic, professional, high quality, masterpiece, stunning, epic, beautiful lighting,
dynamic camera, intense moment, powerful scene. Each is a placeholder for a detail you have not written.

**Camera needs a reason** (Fincher): every move answers "what changed?" — a decision, new information, rising
pressure, a look, a rack to a gesture, a door. If nothing changed, the camera is static. (Confirmed on LTX and
Seedance: unmotivated drifts and push-ins are where framing and identity die.)

**Staging tells the conflict before a line is spoken**: doorway controls the room; standing over seated; shadow is
threat or grief; shared frame without eye contact is broken intimacy.

**Murch's Rule of Six** — when choosing a cut: emotion 51 %, story 23 %, rhythm 10 %, eye-trace 7 %, screen plane
5 %, 3-D space 4 %. Cutting for pace alone is item three; it must serve one and two.

---

## 2. Identity strings (the fix for drift between takes)

One noun phrase, **30–50 words**, that re-specifies a character to a model with no memory. Written once at Gate 3,
stored in the character lock, **pasted verbatim** into every still and video prompt for that character. Never
paraphrased, never shortened for a close-up. Recipe, in order:

1. one age as a number (+ ethnicity where it is a fact about the face)
2. two or three face-structure facts — jaw, eye set, brow, nose, hairline
3. **exactly one checkable landmark** — a mole with a side, a scar with a length, a chipped tooth (this is the QC handle)
4. one hair spec — length, cut, parting or tie-up side
5. one wardrobe anchor, last — garment, colour, material, one detail readable at a distance

Never inside it: mood adjectives, camera or lighting words, celebrity lookalikes, age ranges, "period clothing",
"same as the reference / do not change her face", anything that changes during the story (wet hair, the wound
that grows), or a second character.

Example (47 words): *SIDDHARTHA, 28, north Indian, lean oval face, straight heavy brows, a slightly hooked nose, a full lower lip, a small pale scar through the outer left eyebrow, black hair in a low knot at the nape, in an unbleached white cotton dhoti and shawl with gold armlets.*

**Fifteen things drift** — check before approving any take: face · hair · wardrobe per layer · props (which hand)
· wet/dirt/blood · injury · light direction · time of day · weather · geography (door still on the same wall?) ·
screen direction · eyeline · camera height · palette · lens feel. Progressive states (wet, wounded, the bowl now
empty) live in a per-shot state ledger, never in the identity string.

---

## 3. Failure ladder (spend the cheapest fix first)

Name the failure before touching anything. Buckets, roughly in the order they cost:

| Code | Symptom | First fix |
|---|---|---|
| F2 | nothing moves / only the face moves | prompt edit: one concrete action with an end state |
| F4 / F5 | action ignored / clip ends before the end state | shorten the ask; write the end state; first+last frame |
| F6 | camera moves you did not ask for | `static`, "Camera holds"; delete every motion word but one |
| F1 | identity drifts inside the take | shorter take (cut 40–50 %), one size closer, head turn under 45° |
| F7 | start state contradicts the previous shot's end | state ledger; rebuild the keyframe from the last frame |
| F9 / F11 | new person/object appears / text or watermark | negatives that name the instance, not the category |
| F12 / F16 | light or grade changes mid-clip / between clips | rebuild keyframe; video-to-video regrade; grade in post |
| F15 | mouth and words disagree; room tone fights the space | lip-sync from reference audio; dub the clean line back in post |

Ladder: **L1** prompt edit → **L2** parameter (shorter, less motion, seed) → **L3** regenerate unchanged (budget two
pulls) → **L4** rebuild the keyframe → **L5** re-plan the shot (shorter, closer, simpler, split, first/last frame,
substitute a reaction shot) → **L6** fix in the edit (a 0.5 s trim beats a fourth generation). Three strikes on one
shot → L5, not L3.

---

## 4. What we learned on the Buddha pilot (2026-09-06)
- A narrated montage over stills reads as AI slop; dialogue scenes with coverage read as film. Direct scenes, not shots.
- Seedance 2.5 **re-voices** reference audio during lip-sync and its Hindi phonetics are weak ("पिताजी" → "पिटीजा").
  Keep the picture, duck its track under each line, and lay the clean ElevenLabs line back at the detected offset.
- Only text-only Seedream stills pass Seedance's face filter; frames from Seedance's own output do not.
- Reference audio must be ≥ 1.8 s; reference tasks queue ~12 min; output is 720p (upscale at assembly).
- Whisper timestamps trim leading silence — use RMS speech bursts for caption timing, ASR only for words.

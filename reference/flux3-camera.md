# FLUX 3 camera & style vocabulary — the BFL cheat sheet, folded in (2026-09-06)

Source: BFL's *Examples & Cheatsheet* for FLUX 3 video — https://docs.bfl.ml/guides/prompting_video_camera_terms — 14 categories,
119 terms, each with a rendered demo clip. This file is the studio's working copy: the vocabulary, how the official examples phrase
it, and how it combines with our own doctrine (audio layers, "no on-screen text", identity strings, one move per shot). Read
[flux3.md](flux3.md) first for modes, audio and multi-shot; this page only supplies the nouns.

## How the official examples are built

- **Term first.** Every gallery prompt opens with the camera noun as the shot's identity: *Dutch angle of…*, *Rack focus from … to …*,
  *Whip pan from A to B*, *Lazy Susan shot, …*. The harness that rewrites your prompt reads that leading term as the framing contract.
  (The FAQ says subject-then-camera also works; either order is fine — what matters is the count, below.)
- **Then one visible action, then one or two atmosphere details** (light, weather, particles), then the frame spec written as prose:
  *"…, 10 seconds, 16:9"*. Prose duration/aspect is what steers `--duration auto` / `--ratio auto`; when you pass the flags they are
  API fields and win — keep prose and flags consistent, never contradictory.
- **Two lengths.** The short exploration phrase (5–10 words: *slow pan across pines to reveal a lake at dawn*) and the atmospheric
  one-liner (25–40 words). Start short to find the shot, lengthen to lock it — same as the four formats in flux3.md.
- **One framing term + one movement term + one clear subject action.** The official bad example stacks four (*low aerial handheld orbit
  push-in*) and becomes unreadable. Add at most one lens/optic or one time treatment on top. **This is the cap.**
- **Camera language is optional** in the docs' view — leave it out and the model infers a shot. For us that is an unnamed layer
  (flux3.md: every layer you leave unnamed is a decision you gave away), so name it whenever framing or motion matters, which is
  nearly always in a directed film.
- **Named directors and eras are sanctioned as looks** — the official prompts reach for a Wes Anderson-style tableau, a Wong Kar-wai
  step-printing mood, Busby Berkeley geometry, a 90s camcorder, 16-bit pixel art. Use them as *look* references; brand assets, real
  people and specific films stay out.
- **These are camera phrases, not full prompts.** The demo clips are picture-only demos; every entry below still needs the audio
  layers, the guardrail line ("no on-screen text, no subtitles") and — for people — the identity string.

## The vocabulary

Phrases in the third column are studio-written stubs in the official pattern (term → subject + action → one atmosphere detail).
Finish them with light, audio layers and the guardrail before sending.

### Shot sizes and framing

| Term | Reads as | Studio phrase |
|---|---|---|
| Extreme close-up | one tiny detail fills the frame | *Extreme close-up of a stylus tip touching glass, a bead of ink swelling* |
| Macro | extreme magnification of a very small area | *Macro close-up of frost crystals spreading across a window pane* |
| Close-up | a face, a texture or a single object | *Close-up of a potter's thumbs pressing a rim true* |
| Medium shot | waist up; subject and surroundings balanced | *Medium shot of a tailor pinning a sleeve at the workbench* |
| Cowboy shot | mid-thigh up; hands and hips in frame | *Cowboy shot of a courier at the loading dock, hand resting on the scanner* |
| Full shot | the whole body, head to toe | *Full shot of a fencer saluting alone in an empty hall* |
| Wide shot | full body plus a lot of environment | *Wide shot of a cyclist crossing a salt flat at dusk* |
| Establishing shot | place and scale before any action | *Establishing shot of a fishing village under low cloud, boats coming in* |
| Two shot | two subjects share one frame | *Two shot of a mother and son at a kitchen table, tea steaming between them* |

### Camera angles

| Term | Reads as | Studio phrase |
|---|---|---|
| Aerial | from high above the scene | *Aerial view of a tractor drawing lines across a wet field* |
| Bird's eye (top-down) | straight down, graphic | *Bird's eye top-down view of rowers pulling in unison through green water* |
| High angle | looking down; diminishes or exposes | *High angle on a lone commuter crossing an empty station hall* |
| Eye level | neutral, at the subject's eye height | *Eye level shot of a baker sliding a tray across the counter* |
| Low angle | looking up; scale, dominance | *Low angle on a climber chalking her hands beneath the overhang* |
| Ground level | lens resting on the ground, looking across | *Ground level shot, camera on wet cobbles as boots splash past* |
| Worm's eye | extreme low, looking straight up | *Worm's eye view of cranes swinging above a construction pit* |
| Dutch angle | tilted horizon; unease | *Dutch angle of a night porter walking a tilting hotel corridor* |
| Profile shot | strict side-on view | *Profile shot of a woman at a bus window, streetlights strobing across her face* |
| Over-the-shoulder | past a foreground shoulder to the subject | *Over-the-shoulder view of an editor reading a wall of index cards* |
| POV | the character's own eyes | *POV pushing through a curtain of hanging laundry into a courtyard* |
| Object POV | the world seen from an object | *Object POV from inside a mailbox, the flap opens to a face peering in* |
| Tableau | static, symmetrical, staged wide | *Tableau shot, static symmetrical wide of a pastel launderette, staff lined up deadpan* |
| Fourth wall | subject notices and addresses the lens | *Breaking the fourth wall, the barista pauses mid-pour, looks at the lens and speaks* |
| Voyeur | hidden, obstructed spying view | *Voyeur shot through half-closed blinds at a man rehearsing a speech* |

### Composition

| Term | Reads as | Studio phrase |
|---|---|---|
| Leading lines | lines in frame pull the eye | *Leading lines of a pier's boards running out to a single figure* |
| Center framing | subject locked dead centre | *Center-framed portrait of a drummer under one overhead lamp* |
| Rule of thirds | subject off-centre for balance | *Swimmer framed on the right third against an empty pool* |
| Symmetry | mirrored shapes; precision or tension | *Symmetrical school corridor, one child standing still at the vanishing point* |
| Negative space | open space isolates the subject | *A single red kite against a vast flat grey sky* |
| Frame within frame | an in-scene opening frames the subject | *Frame within frame, a chef glimpsed through the pass hatch* |
| Foreground occlusion | blurred foreground objects add depth | *Foreground occlusion, two friends talking seen past out-of-focus market crates* |
| Silhouette | dark subject against bright light | *Silhouette of a surfer walking up the beach into low sun* |
| Reflection framing | subject composed in a reflective surface | *Reflection framing of a dancer in a rain puddle, ripples breaking her outline* |

### Camera movements

| Term | Reads as | Studio phrase |
|---|---|---|
| Pan | rotates left/right from a fixed point | *Slow pan across the workshop shelves to reveal the finished chair* |
| Tilt | rotates up/down | *Tilt up from muddy trainers to a rain-soaked grin* |
| Dolly in | camera physically pushes closer | *Dolly in toward a pianist in the beat before the first chord* |
| Tracking shot | moves alongside the subject | *Tracking shot beside a greyhound at full stretch through wet grass* |
| Trucking | slides laterally past the scene | *Trucking shot, camera slides past a night market, steam rising from stalls* |
| Arc shot | sweeps a semicircle around the subject | *Arc shot gliding a half circle around two people under one umbrella* |
| Orbit | circles the subject | *Slow orbit around a bronze bust in blowing snow* |
| Crane / boom | rises or lowers on an arm | *Crane boom shot rising from a doorstep up the terrace to the rooftop garden* |
| Pedestal | camera moves straight up or down | *Pedestal shot rising along a wall of archive drawers in warm lamplight* |
| Push through | passes through a gap into a new space | *Push through a keyhole into a candlelit map room* |
| Steadicam follow | smooth stabilised follow | *Steadicam follow behind a nurse weaving through a busy ward* |
| Handheld | loose, organic motion | *Handheld camera trailing a runner-up through the backstage corridor* |
| Whip pan | fast pan that blurs between subjects | *Whip pan from the bowler's release to the batsman's swing* |
| Dolly zoom | dolly and zoom opposed; the background warps | *Dolly zoom on a man's face in a hallway as the walls stretch away* |
| Camera roll | rotates around the lens axis | *Camera roll, a full 360° around its own axis as the skater clears the gap* |
| Snorricam | rig on the actor; the world sways, the face stays pinned | *Snorricam shot, camera rigged to her chest as the party sways behind her* |
| Locked-on | subject rigidly fixed, background streaks | *Locked-on shot, her face perfectly stable while the platform whips past* |
| Lazy Susan | subject on a turntable, camera fixed | *Lazy Susan shot, the bottle turning slowly on a turntable, camera locked, black backdrop* |

### Focus

| Term | Reads as | Studio phrase |
|---|---|---|
| Shallow depth of field | subject sharp, background soft | *Shallow depth of field on rain sliding down a bus window* |
| Deep focus | front to back all sharp | *Deep focus across a hardware store from the front counter to the back door* |
| Rack focus | focus shifts between planes | *Rack focus from the ring on the table to the woman at the door* |
| Split diopter | near and far both sharp, seam between | *Split diopter keeping the hidden child razor sharp and the far door equally sharp* |
| Focus breathing reveal | blur slowly resolves into the subject | *Focus breathing reveal, soft blur resolving into a face under a streetlight* |
| Tilt shift | selective focus; miniature look | *Tilt shift shot of a harbour town, toy-like ferries crossing* |

### Lenses and optics

| Term | Reads as | Studio phrase |
|---|---|---|
| Wide angle (24 mm) | exaggerated space, edge distortion | *Wide angle 24 mm lens following a courier through a narrow alley, walls looming* |
| Telephoto compression | flattens depth, stacks planes | *Telephoto compression stacking a line of red buses into flat layers, heat shimmer* |
| Fisheye | extreme curved distortion | *Fisheye lens inside a skate bowl, the horizon bending around the camera* |
| Anamorphic flares | horizontal streaks, oval bokeh | *Anamorphic flares streaking across a night runway as a jet taxis past* |
| Macro lens | extreme magnification of detail | *Macro lens on a watch escapement ticking, brass glinting in shallow focus* |
| Probe lens | snorkel lens weaving low through tight spaces | *Probe lens shot, snorkel camera gliding between cups, toast and dripping honey* |
| Halation | glowing halos bloom around highlights | *Halation film look, red-orange halos blooming around candle flames* |
| Parallax | depth layers slide at different speeds | *Parallax shot, fence posts, trees and far hills sliding against each other* |
| Vignette | darkened edges, bright centre | *Heavy vignette closing around a lamplit face reading letters* |

### Shutter and time

| Term | Reads as | Studio phrase |
|---|---|---|
| Slow motion | action stretched below real time | *Slow motion of a dog shaking lake water off, droplets fanning out* |
| Speed ramp | speed shifts inside one shot | *Speed ramp as the racket meets the ball, time slowing at impact then snapping back* |
| Fast motion | undercranked, accelerated | *Fast motion of a station hall, commuters streaming while one traveller stands still* |
| Timelapse | long spans compressed | *Timelapse of fog pouring over a ridge into the valley at dawn* |
| Long exposure look | motion smears into light trails | *Long exposure look, a night cyclist's lights smearing into trails* |
| Bullet time | frozen instant, camera orbits through it | *Bullet time shot, flour frozen mid-air around a baker while the camera orbits* |
| Freeze frame | subject freezes, camera keeps moving | *Freeze frame, the diver halts mid-air while the camera keeps dollying around him* |
| Boomerang | short action forward, then reversed, looping | *Boomerang loop of a cork popping and returning to the bottle* |
| Step printing | stuttering, smeared motion trails | *Step printing effect, a dancer in a neon alley leaving ghosted trails* |
| Cinemagraph | a still with one small looping motion | *Cinemagraph, a frozen café scene where only the steam from one cup keeps rising* |

### Lighting

| Term | Reads as | Studio phrase |
|---|---|---|
| Rim light | backlight outlines the edge | *Rim light outlining a rower's shoulders, background falling to black* |
| Chiaroscuro | strong light against deep shadow | *Chiaroscuro lighting, a cellist under a single beam, shadow carving the bow strokes* |
| Hard light | sharp-edged shadows, high contrast | *Hard light through venetian blinds striping a detective's desk* |
| Golden hour | warm, low sun, backlit | *Golden hour backlight over barley, wind moving the stalks in waves* |
| Neon practicals | in-scene coloured sources | *Neon practicals washing a face in shifting pink and cyan from the sign outside* |
| Volumetric light | visible beams, god rays through haze | *Volumetric light, god rays through a dusty barn as a farmer walks the beams* |
| Haze | thick atmosphere shows the light shafts | *Atmospheric haze, a warehouse with shafts from high windows, one figure walking through* |
| Spotlight | a single beam isolates the subject | *A single spotlight following a singer across a dark stage, dust in the cone* |
| Light flash | strobing flashbulb bursts freeze motion | *Rapid paparazzi flashes strobing across a red carpet, each burst freezing a pose* |
| Projections | projected imagery plays across the subject | *Vintage film projections flickering across a woman's calm face* |
| Underwater light | rippling caustics on surfaces | *Underwater light caustics rippling across a pool floor as a swimmer glides through* |

### Shot transitions (inside one generation)

| Term | Reads as | Studio phrase |
|---|---|---|
| Match cut | a shape or motion carries across the cut | *Match cut from a spinning coin to a spinning ceiling fan, the rotation carrying over* |
| Whip transition | a whip pan hides the cut | *Whip transition, the camera whips out of the kitchen and lands in the dining room* |
| Foreground wipe | a passing object wipes to a new scene | *Foreground wipe as a tram fills the frame and clears onto a different street* |
| Object portal | the camera dives into an object into a new scene | *The camera dives into a teacup, the swirl dissolving into an autumn forest* |
| Pass-through | one continuous move threads several spaces | *A gliding pass-through from the study, out the window, into the rainy street, one move* |
| Jump cut | abrupt discontinuous cuts, same framing | *An anxious monologue to camera with abrupt jump cuts, position snapping between phrases* |
| Quick cuts | rapid rhythmic montage of very short shots | *Energetic quick cuts chop the morning routine into eight snappy shots* |
| Screen-in-screen | recursive screen within a screen | *Infinite screen-in-screen recursion, a viewer watching herself watching* |

### POV and specialty rigs

| Term | Reads as | Studio phrase |
|---|---|---|
| Drone FPV | fast, agile first-person drone | *Drone FPV diving off a dam wall and skimming the spillway* |
| Bodycam | chest-mounted POV, bobbing | *Bodycam POV jogging up a stadium tunnel toward daylight, camera bobbing per stride* |
| Dashcam | fixed in-car view of the road | *Dashcam view of deer crossing a snowy road at dusk, wipers sweeping* |
| Mirror POV | subject seen in a mirror | *Mirror POV, a man knotting a tie, looking straight into the bathroom mirror* |

### Aspect and format

| Term | Reads as | Studio phrase |
|---|---|---|
| Cinemascope (21:9) | ultra-wide anamorphic frame | *Cinemascope 21:9 frame, two figures facing off across a dry lakebed* (+ `--ratio 21:9`) |
| Vertical (9:16) | tall, mobile-first frame | *Vertical 9:16 frame, camera tilting up the rungs of a fire tower* (+ `--ratio 9:16`) |
| Vintage (4:3) | boxy, retro camcorder | *Vintage 4:3 home video of a 90s birthday, grainy camcorder look* (+ `--ratio 4:3`) |
| Split screen | two shots side by side | *Split screen, two callers in different cities laughing on the phone at once* |

### VFX and transformation

| Term | Reads as | Studio phrase |
|---|---|---|
| Double exposure | two images blended in one frame | *Double exposure blending a profile portrait with a pine forest drifting inside it* |
| Morphing | one subject fluidly becomes another | *Seamless morphing of one face through four ages under soft studio light* |
| Levitation | objects or people float weightlessly | *Quiet levitation, books and cups drifting around a woman still reading* |
| Kaleidoscope | mirrored, repeating symmetry | *Overhead kaleidoscope symmetry multiplying a dance troupe into a mandala* |
| Slit scan | motion smeared into flowing time ribbons | *A galloping horse stretched into slit-scan ribbons across the frame* |
| Datamosh | glitched, smearing pixel corruption | *On the beat drop the frame erupts in datamosh smear, colours bleeding* |
| X-ray | see-through view of inner structure | *X-ray view of a mechanical hand flexing, gears glowing blue-white on black* |

### Art direction

| Term | Reads as | Studio phrase |
|---|---|---|
| Dreamcore | liminal, nostalgic, quietly wrong spaces | *Dreamcore emptiness, endless pastel corridors under a blown-out sky, a swing moving with no wind* |
| Dystopian | bleak, oppressive future | *A dystopian megacity in relentless rain, drones sweeping searchlights over the crowd* |
| Magical realism | gentle magic inside an ordinary scene | *Magical realism in a corner café, paper lanterns drifting between tables unremarked* |
| Maximalism | dense, ornate, overloaded design | *Opulent maximalism, a salon crowded with gilt mirrors and stacked paintings, camera gliding through* |
| Diorama | tilt-shift model world | *A diorama miniature town waking up, felt cars and handmade houses under a lamp* |

### Animation and media

| Term | Reads as | Studio phrase |
|---|---|---|
| Stop motion | handmade frame-by-frame clay | *Stop motion claymation, a breakfast table setting itself in jerky handmade frames, fingerprints visible* |
| Pixel art | retro low-res 16-bit | *Retro pixel art, a 16-bit city at sunset with dithered gradients and sprite pedestrians* |
| Zoetrope | pre-cinema spinning-drum animation | *A spinning zoetrope flickering painted horses to life through its slits* |
| Kinetic typography | animated text is the visual | *Kinetic typography building a skyline from stacked words* — see the studio note below |

## What this changes in the studio doctrine

1. **Transitions have names; `HARD CUT.` is only the default.** Match cut, whip transition, foreground wipe, object portal, pass-through
   and jump cut are nouns the harness knows. When a cut should be *motivated*, write the transition instead of a hard cut:
   *"SHOT ONE: … MATCH CUT on the rotation into SHOT TWO: …"*, *"a passing tram wipes to …"*. Fewer, named transitions beat more hard cuts.
   (Two of these — foreground wipe and pass-through — are the "Lumina" technique already in learnings.md; now they are official vocabulary.)
2. **Two multi-shot registers.** Narrative coverage = `SHOT N … HARD CUT.` at ~5 s per shot (flux3.md rule). Rhythmic montage = *"quick
   cuts … N snappy shots"* — the official demo asks for eight shots in 10 s over one percussive bed. Use the montage register only without
   dialogue and with one audio bed named once. *[official example; not yet run by us — verify the cut count with `select='gt(scene,0.3)'`.]*
3. **Product-film rigs are first-class terms:** Lazy Susan (product turns, camera locked), probe lens (snorkel through a still life),
   macro lens on mechanisms, pedestal along a shelf, locked-on. Reach for these before inventing a move for a packshot.
4. **Time is a treatment you can name:** speed ramp at the impact, freeze frame with a moving camera, bullet time, boomerang loop,
   cinemagraph (a still with one motion — the cheapest "living hero still"), step printing for memory/night.
5. **Talking-to-camera grammar:** fourth wall (subject notices the lens and speaks), mirror POV, jump-cut confessional. Combine with the
   dialogue rules in flux3.md — visible speaker, exact words in quotes, delivery, "no on-screen text, no subtitles".
6. **Lighting nouns are the i2v `[LIGHT CHANGE]` slot:** *the neon practicals shift from pink to cyan*, *a single spotlight finds her*,
   *hard light through the blinds crawls across the desk*. A named light change is motion the model renders well on a locked frame.
7. **Kinetic typography is a documented capability.** FLUX 3 will animate words as the picture. The studio rule stands — brand type,
   prices, claims and CTAs are composited in HyperFrames — but a typographic *texture* (words as skyline, letters as rain) can be
   generated when the exact spelling is not a brand asset. Check every letter before it ships.
8. **Format words double as aspect:** *Cinemascope 21:9 frame* + `--ratio 21:9`; *vertical 9:16* + `--ratio 9:16`; *vintage 4:3
   camcorder* + `--ratio 4:3`. Prose and flag must agree; a 16:9 still with a 21:9 flag is cropped.
9. **The stacking cap** goes into review: any prompt with three or more camera terms in one phrase is sent back before it is generated.

## Quick picks — intent → terms

| You want | Reach for |
|---|---|
| Dread, wrongness | Dutch angle · slow dolly in · hard light or a voyeur view |
| Intimacy | close-up · 70 mm shallow depth of field · rim light or neon practicals |
| Scale, arrival | establishing wide · crane or pedestal rising · volumetric light |
| Energy | whip pan · handheld · speed ramp · quick cuts (no dialogue) |
| Product hero | Lazy Susan · probe lens · macro lens · spotlight on a black backdrop |
| A reveal | push through · focus breathing reveal · foreground wipe · tilt up |
| Time passing | timelapse · the same locked frame with light cues across hard cuts · quick cuts |
| Memory, dream | double exposure · halation · step printing · dreamcore |
| Someone talks to us | fourth wall · eye level · medium or close-up · jump cuts if it is a vlog |
| Two people | two shot · over-the-shoulder · arc shot around them |

## Two full prompts built from the vocabulary

**Product, no people (i2v, 8 s, hd, 1:1 still):**
> Use this image as the first frame. Lazy Susan shot: the bottle turns slowly on a black turntable while the camera stays locked, a single
> spotlight from top left, hard light catching the embossed glass. Hold the label, the backdrop and the light exactly as in the still.
> Audio: the faint whir of the turntable, studio room tone. No music, no dialogue, no on-screen text.

**Someone talks to us (t2v, 10 s, 16:9):**
> Breaking the fourth wall, eye level medium shot: a barista in her thirties, cropped grey hair, navy apron, pauses mid-pour, looks straight
> into the lens and says, dry and half-amused, "You're early." Neon practicals from the window wash her face pink and cyan. Camera locked.
> Ambience: espresso machine hiss, rain on the glass. No music, no announcer delivery, no on-screen text, no subtitles.

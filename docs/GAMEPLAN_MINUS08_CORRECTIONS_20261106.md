# -08 Correction Game Plan — 2026-11-06

Reference images used: `Azazel.jpg` (operator + goat + fiery angel)
Source: operator notes, session 2026-11-06

---

## STATUS KEY
- `[ ]` not started
- `[~]` prompt written, needs render
- `[x]` done

---

## ACT 2 — CLIFF TOP (cliff_top_night)

### Scratch scene background
- `[~]` **Remove monster claw from scratch scene.** Background shows symbols scratched into rock — no claw, no creature, no hand in the image. The rock surface is the subject. Characters and the iguana are around it as avatars.
- `[~]` **Only the iguana is in the party line this scene.** Everyone else is at the top but the scratch action is the iguana's moment. Remove all other party sprites.
- `[ ]` **Horizontal flip logic.** When the scratch is the focus (cliff_top_night frames), flip party sprites so they face the scratch (facing right toward center, or facing each other). The iguana faces the scratch surface. Add `FLIP_FRAMES` set to `draw_frame` — for frames in that set, `pygame.transform.flip(img, True, False)` before blit.

---

## ACT 3 — ANTECHAMBER (skeleton combat)

### Background
- `[~]` **Remove all figures from antechamber background PNG.** Background = empty room, bones in niches, torch, narrow passage. Party and skeleton handled as sprites only.

### Party order
- `[ ]` **Draavio must be in front (position 1 / leftmost).** Current CHAR_POSITIONS has Merit at pos 1. In the antechamber and all combat scenes Draavio is at the front. Fix CHAR_POSITIONS so Draavio = x≈20 (front) and other chars shift right. Merit stays small/short but behind Draavio.

### Skeleton combat sequence — DD-lite action frames
Needed frame IDs in narration (add `~~FRAME:~~` annotations):

| Frame ID | Action | New sprite needed? |
|---|---|---|
| `antechamber` | Skeleton stands in niche, tongue out, facing party | `skeleton_tongue` ✓ |
| `skeleton_advance` | Skeleton moves forward (mid-stride toward party) | `skeleton_tongue` (reuse, different pos) |
| `skeleton_lick_draavio` | Skeleton licks Draavio — tongue extends left | `skeleton_tongue_lick` ✓ |
| `skeleton_slam_1` | First slam — fists raised, Draavio taking hit | `skeleton_tongue_slam` ✓ |
| `skeleton_slam_2` | Second slam | same |
| `pyrrhon_scorching` | Pyrrhon casts — arm raised, fire implied | Pyrrhon sprite + glow |
| `njala_hex` | Njála hexes — coin visible, misfortune applied | Njála sprite + glow |
| `draavio_falchion` | Draavio slices down — falchion raised | `draavio` sprite + glow (weapon implied by prompt) |
| `antechamber_post` | Post-combat, party standing | standard party line |

- `[ ]` Add these `~~FRAME:~~` annotations to `-08_narration.md` at the correct dialogue beats
- `[ ]` Add `FRAME_ENEMIES` entries for each combat frame ID
- `[ ]` Draavio's falchion must be visible in his sprite — check `draavio` prompt, add if missing
- `[ ]` **Who is the man in the background of the current antechamber PNG?** Delete current `antechamber.png` (already done). New prompt = empty room only.

---

## ACT 4 — GIFT ROOM (gargoyle combat + link on altar)

### Gargoyle combat — DD-lite action frames

| Frame ID | Action |
|---|---|
| `gift_room` | Gargoyle on ledge, watching — DD avatar right side |
| `draavio_bow_miss` | Draavio fires bow, misses — avatar action |
| `gargoyle_dive` | Gargoyle launches from ledge toward party |
| `gargoyle_combat` | Gargoyle in melee — DD avatar at center-right |
| `gift_room_heal` | Post-combat: party standing, heals applied |

- `[ ]` Add `~~FRAME:~~` annotations in narration
- `[ ]` Add `gargoyle_dive` sprite to ENEMY_PROMPTS (gargoyle mid-dive, wings spread, toward left)
- `[ ]` All actions including heals need representation
- `[ ]` **More people in the background** — update gift_room BG prompt to show corpses of prior visitors, scattered bodies, evidence of previous parties
- `[ ]` Draavio needs a bow-draw pose — consider `draavio_bow` sprite (or reuse `draavio` with note)

### Link on altar
- `[~]` Already have `special_link_on_altar`. **Only Draavio in the room by this point.** All other party members absent. `draw_frame` must suppress party line for `link_on_altar` frame.
- `[ ]` **Add new background between corridor and altar:** `coffin_uncovered` — a coffin partly dug out from rubble, a secret door visible in the stone behind it. DD style. Add to `BG_PROMPTS` and `SPECIAL_FRAME_PROMPTS`.
- `[ ]` **Altar interaction frame:** Draavio DD-style at the altar (interacts — hand on altar, examining). Add `draavio_altar` frame to `FRAME_ENEMIES` or special frames logic.

---

## ACT 5 — SECRET CORRIDOR

- `[ ]` Add `coffin_uncovered` background (Draavio finds coffin + secret door). New BG_PROMPTS entry.
- `[ ]` Add `secret_door_found` frame where Draavio stands at the open secret door alone.

---

## ACT 6 — CIRCLE ROOM (crab creature interaction)

### Circle room background — REMAKE
- `[~]` Current angle is wrong: looking inward at angle doesn't allow DD party-left / crab-right layout
- `[~]` **New prompt written** (horizontal chamber, party left, crab right). Delete old `circle_room.png`.
- `[ ]` Verify new PNG when rendered: goats must be in the background near the entrance (left), crab creature's chalk circle must be on the right side with open floor between

### Crab creature interaction sequence

| Frame ID | Action |
|---|---|
| `circle_room` | Crab creature in chalk circle on right. Goat pen left-background. Party left. |
| `draavio_gesture_njala` | Draavio turns to gesture at Njála (faces LEFT toward party — flip his sprite) |
| `njala_vial` | Njála holds vial out toward Draavio — glow on Njála |
| `draavio_approach` | Draavio moves toward crab creature center |
| `crab_interact` | Draavio at crab creature — DD interaction pose |

- `[ ]` Add `~~FRAME:~~` annotations in narration
- `[ ]` `draavio_gesture_njala` needs Draavio facing left (flip) — add to `FLIP_FRAMES`
- `[ ]` **Dr. Drake form check:** Joey is iguana in all circle room scenes. Verify `joey_is_iguana` covers act 6.

---

## ACT 7-9 — CIRCLE ROOM TRAP / WAIT (were-soldiers)

### Camping scene background
- `[ ]` **Remove all people from circle_room_trap background.** Background = empty chamber, broken chalk circle, smooth stones at trap positions. Avatars handle all figures.
- `[ ]` **Resting state poses.** Party avatars in sitting/resting variants around an implied campfire circle. Need sitting sprites OR render a "seated ring" as a special frame with avatars arranged in arc:
  - Draavio sitting (add `draavio_rest` to CHAR_PROMPTS)
  - Njála sitting (add `njala_rest`)
  - Merit sitting (`merit_rest`)
  - Pyrrhon sitting (`pyrrhon_rest`)
  - **Iguana** — iguana is simply the iguana avatar at rest size. Not a giant. Normal size. Sitting among them.
- `[ ]` Add `RESTING_FRAMES` set; in `draw_frame`, if frame in `RESTING_FRAMES` use `_rest` sprite variant when available

### Were-soldier sequence
The user says: were-soldiers are handwaved as "flailing around" — no detailed combat.

| Sprite | State |
|---|---|
| `were_soldier_human` | Composed — upright, glitterdust outline |
| `were_soldier_scent` | Scent hits — grabbing eyes, animalistic breaking through |
| `were_soldier_crumpled` | Down |

- `[~]` Prompts written already
- `[ ]` Four unique researcher avatars needed BEFORE were-soldier sequence:
  - `researcher_1` through `researcher_4` — distinct people, academic gear, underground field clothes
  - Then `researcher_sick` — each one in distress (same 4, sick versions)
  - Then `researcher_crumpled` — collapsed versions
- `[ ]` Add to ENEMY_PROMPTS

### Draavio return — dream sequence
- `[ ]` **Draavio appears mid-conversation in random positions** (DD action dream). Three frames:
  - `draavio_strike_1` — Draavio in foreground left, pointing at were-soldier (center), striking down
  - `draavio_strike_2` — same, different position
  - `draavio_strike_3` — same again
- `[ ]` Add `~~FRAME:draavio_strike_1~~`, `~~FRAME:draavio_strike_2~~`, `~~FRAME:draavio_strike_3~~` in narration at the cadence beats
- `[ ]` These frames show: party (left, sitting/resting) + were-soldiers (right) + Draavio ghost/foreground figure
- `[ ]` Logic: for `draavio_strike_*` frames, render Draavio sprite at random foreground position (large, mid-screen) with amber glow

---

## ACT 10 — CIRCLE ROOM BATTLE (flesh golem)

- `[~]` `flesh_golem_dd` prompt written — very large, stitched, faces left
- `[ ]` Party line: iguana (not doctor) on left — verify `joey_is_iguana = True` for act 10
- `[ ]` Flesh golem renders as DD avatar on right
- `[ ]` Were-soldier sprites cycle through states as battle progresses

---

## PEACOCK WOMAN (within battle sequence)
- `[~]` `peacock_woman` and `peacock_woman_dust` prompts written
- `[ ]` Add `~~FRAME:peacock_intro~~` and `~~FRAME:peacock_fades~~` in narration at exact dialogue beats
- `[ ]` She does nothing wrong. Her avatar must be clearly composed, non-threatening. The glitterdust outline that follows is the injustice — make that legible visually.
- `[ ]` Add framing note in GAMEPLAN: *"She represents the children in the concentration camps in South Africa: faded flowers tossed away. Her response is estimated."* This is the moral context of the glitterdust moment.

---

## ACT 11-12 — CIRCLE ROOM TRIAL (Azazel / archivist)

### Archivist sprite — update prompt
- `[~]` Current `azazel_archivist` prompt written. **Needs update to match `Azazel.jpg`:**
  - Massive fire wings spread wide — full HD illustration style
  - Male figure, powerful build, standing in fire
  - DD painting style applied over this reference
  - The operator figure (back to viewer, glowing tablet) is NOT in the sprite — that's the party/Draavio
  - The goat with red collar IS present in the archivist scene (separate `talking_goat_dd` avatar)
- `[ ]` Update `azazel_archivist` prompt to reference: "massive spreading fire wings, male figure standing in ring of flame at base of oak, looking forward (facing left toward party), wings fill the frame behind him"
- `[ ]` Archivist is looking AT the party — not away. Fix orientation in prompt.

### Scratch / Matthew 25:18 scene
- `[ ]` **Iguana center** for this scene. Not Draavio at front — iguana is the focal avatar.
- `[ ]` **Draavio taking notes** — need `draavio_notes` sprite: Draavio with scroll/paper, quill or pen, writing. Looking down at the notes, not at the archivist.
- `[ ]` **Njála listening** — `njala_listen` sprite: Njála turned slightly, coin still, attentive posture.
- `[ ]` Add `~~FRAME:scratch_iguana~~` annotation at the Matthew 25:18 scratch beat in narration
- `[ ]` Add `~~FRAME:language_invent~~` annotation at the language invention scene
- `[ ]` In `draw_frame`: for `scratch_iguana` and `language_invent` frames, center the iguana avatar; Draavio rendered in notes pose; Njála in listen pose

### Goat with porthole handkerchief
- `[~]` `goat_porthole` sprite prompt written
- `[ ]` Add DD interaction frames: Draavio or party member crouches toward goat, examines handkerchief
- `[ ]` Add `~~FRAME:goat_porthole~~` annotation in narration

---

## GENERAL / CROSS-SCENE

### Horizontal flip system
- `[ ]` Add `FLIP_FRAMES: set[str]` to build script
- `[ ]` In `draw_frame`, after loading char plate, check if frame in FLIP_FRAMES and flip relevant sprites
- `[ ]` Frames to flip party sprites: `cliff_top_night` scratch scenes (party faces scratch = faces right, so no flip needed — they already face right), `draavio_gesture_njala` (Draavio faces left toward Njála)
- `[ ]` Frames to flip enemy/NPC sprites: none (they already face left by design)

### Party front position — Draavio must be first
- `[ ]` Update `CHAR_POSITIONS` so Draavio = pos 1 (x≈20, frontmost)
- `[ ]` Shift Merit, Njála, Pyrrhon positions right accordingly
- `[ ]` Current layout has Merit at front — this is wrong for combat scenes

### Characters removed from backgrounds
- `[x]` `antechamber.png` — deleted, new prompt = empty room
- `[x]` `cliff_top_night.png` — deleted, new prompt = empty stone
- `[x]` `gift_room.png` — deleted, new prompt = room only (gargoyle on ledge is background set-dressing, not a sprite)
- `[x]` `circle_room.png` — deleted, new prompt = horizontal layout, no figures
- `[ ]` `circle_room_battle.png` — check current PNG, remove any figures
- `[ ]` `circle_room_trial.png` — check current PNG, archivist should NOT be in background (he is an avatar)

### Dr. Drake form audit (every act)
| Act | Scene | Expected form |
|---|---|---|
| 0 | Table | `pstand_joey` (doctor's coat) |
| 1 pre-wildshape | mountain_road | `raymora_doctor` |
| 1 post-wildshape | mountain_road / cliff | `raymora_iguana` |
| 2 | cliff_top_night | `raymora_iguana` |
| 3 | antechamber | `raymora_iguana` |
| 4 | gift_room | `raymora_iguana` |
| 5 | secret_corridor | `raymora_iguana` |
| 6-12 | all subsequent | `raymora_iguana` |

---

## RENDER QUEUE (sprites to generate)

Priority order (generate in this sequence):

1. **New backgrounds** (blocking everything else):
   - `mountain_road` (low upward angle) ← deleted
   - `cliff_top_night` (empty stone) ← deleted
   - `antechamber` (empty room) ← deleted
   - `gift_room` (room + gargoyle on ledge as set-dressing) ← deleted
   - `circle_room` (horizontal, no figures) ← deleted
   - `coffin_uncovered` (new)
   - `circle_room_trap` (verify people-free)
   - `circle_room_battle` (verify people-free)
   - `circle_room_trial` (verify archivist absent)

2. **Player standing sprites** (already deleted, new prompts written):
   - `pstand_lisbeth_*` × 3 (Lisbeth Salander look)
   - `pstand_sheldon_*` × 3 (Flash t-shirt)
   - `pstand_joey_*` × 3 (white doctor's coat)
   - `pstand_vincent_*` × 3 (double-breasted suit)

3. **Character sprites** (already deleted or new):
   - `njala` (rogue-lean, no dress)
   - `pyrrhon` (tall wizard, no crossbow)
   - `raymora_doctor` (tunic-scrubs + stethoscope) ← new
   - `raymora_iguana` (clean anatomy)

4. **Enemy sprites** (all new):
   - `skeleton_tongue`, `skeleton_tongue_lick`, `skeleton_tongue_slam`
   - `gargoyle_dd`, `gargoyle_dive`
   - `crab_creature`
   - `flesh_golem_dd`
   - `were_soldier_human`, `were_soldier_scent`, `were_soldier_crumpled`
   - `peacock_woman`, `peacock_woman_dust`
   - `talking_goat_dd`, `goat_porthole`
   - `azazel_archivist` (update prompt to match Azazel.jpg)

5. **Action / note-taking sprites** (new):
   - `draavio_notes` (Draavio writing, scroll in hand)
   - `njala_listen` (Njála attentive, listening)
   - `draavio_rest`, `njala_rest`, `merit_rest`, `pyrrhon_rest` (seated/resting)
   - `researcher_1` through `researcher_4` (four unique researchers)
   - `researcher_sick`, `researcher_crumpled`
   - `gargoyle_dive`

---

## NARRATION ANNOTATION QUEUE

Annotations still needed in `-08_narration.md` (find correct dialogue beats):

- `~~FRAME:skeleton_advance~~` — skeleton moves toward party
- `~~FRAME:skeleton_lick_draavio~~` — lick action
- `~~FRAME:skeleton_slam_1~~` — first slam
- `~~FRAME:skeleton_slam_2~~` — second slam
- `~~FRAME:pyrrhon_scorching~~` — Pyrrhon casts scorching ray
- `~~FRAME:njala_hex~~` — Njála applies misfortune hex
- `~~FRAME:draavio_falchion~~` — Draavio falchion strike down
- `~~FRAME:draavio_bow_miss~~` — Draavio bow miss in gift_room
- `~~FRAME:gargoyle_dive~~` — gargoyle launches
- `~~FRAME:gift_room_heal~~` — post-combat heals
- `~~FRAME:coffin_uncovered~~` — Draavio finds coffin + secret door
- `~~FRAME:draavio_altar~~` — Draavio at altar
- `~~FRAME:draavio_gesture_njala~~` — Draavio gestures to Njála
- `~~FRAME:njala_vial~~` — Njála hands vial
- `~~FRAME:crab_interact~~` — Draavio at crab creature
- `~~FRAME:peacock_intro~~` — peacock woman avatar
- `~~FRAME:peacock_fades~~` — glitterdust outline
- `~~FRAME:draavio_strike_1~~`, `~~FRAME:draavio_strike_2~~`, `~~FRAME:draavio_strike_3~~` — return dream
- `~~FRAME:scratch_iguana~~` — Matthew 25:18 scratch, iguana center
- `~~FRAME:language_invent~~` — language invention, Draavio notes + Njála listens
- `~~FRAME:goat_porthole~~` — goat with handkerchief interaction

---

## DONE THIS SESSION (2026-11-06)

- `[x]` Player sprite prompts rewritten (Lisbeth Salander, Flash Sheldon, Dr. Drake Joey, Gattaca Vincent)
- `[x]` `raymora_doctor` sprite added (tunic-scrubs + stethoscope)
- `[x]` Enemy sprite prompts written (14 original + 8 new: gargoyle_dive, researcher_1–4, researcher_sick, researcher_crumpled)
- `[x]` Mountain road background — extreme low-angle cliff wall
- `[x]` Circle room — horizontal layout for DD-style
- `[x]` Cliff top night — empty stone (no embedded figures)
- `[x]` Antechamber, gift_room backgrounds — figures removed
- `[x]` circle_room_battle, circle_room_trial — figures removed from BG prompts
- `[x]` coffin_uncovered background added
- `[x]` azazel_archivist prompt updated — massive spreading fire wings, facing left
- `[x]` CHAR_POSITIONS — Draavio at front (x=20), Merit behind
- `[x]` FLIP_FRAMES set + draw_frame update (draavio_gesture_njala, scratch scenes)
- `[x]` RESTING_FRAMES set + draw_frame update (circle_room_trap, were-soldier wait)
- `[x]` draavio_notes, njala_listen, 4 rest sprites added to CHAR_PROMPTS
- `[x]` FRAME_ENEMIES expanded (antechamber seq, gift room seq, gargoyle_dive, researchers, peacock, draavio strikes, scratch)
- `[x]` Narration: 20 new ~~FRAME:~~ annotations (njala_hex, skeleton_lick_draavio, skeleton_slam_1, draavio_falchion, antechamber_post, gargoyle_dive, draavio_bow_miss, gargoyle_combat, gift_room_heal, coffin_uncovered, draavio_gesture_njala, njala_vial, crab_interact, goat_porthole, peacock_intro/fades, were_soldier states, draavio_strike_1/2/3, scratch_iguana, language_invent)
- `[x]` Scratch override in draw_frame — iguana centered, draavio_notes, njala_listen for scratch_iguana/language_invent frames
- `[x]` Stills render started (running — mountain_road ✓, cliff_top_night ✓, antechamber ✓)
- `[x]` Narration: `merlin_alone`, `party_table`, climb frames, wildshape frame
- `[x]` Draw_frame: Feynman apart/above, merlin_alone mode, climb disappearance, wildshape swap, enemy sprite rendering
- `[x]` Azazel reference image found (`/home/dylanmccapes/dev/Azazel.jpg`)
- `[x]` Deploy pipeline fixed (catalog had wrong filename for -08 video)

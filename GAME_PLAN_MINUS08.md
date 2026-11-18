# GAME_PLAN — Page −08: The Archive at the Mountain

**Filed:** 2026-11-06  
**Source document:** `src/phase2/-08.md` (2151 lines)  
**Target build:** `tools/build_minus08_video.py`  
**Output:** `video/minus08/-08_the_archive.mp4`

---

## 0. Scope & vision

−08 is a Pathfinder session, narrated in full. The style departs from every prior page:

- **Pre-game** (before first die): still portrait shots of the players at the table. The Witch of the Rivers character uses her existing artwork as the reference for her portrait — that is what she looks like in the opening scene. Not a background; the artwork defines the sprite.
- **In-game**: full Darkest Dungeon aesthetic. Painterly stone corridors, dim torchlight, party arrayed left-facing-right against enemies. Transitions between scenes are DD-style chapter cards (black + thin serif title).
- **Feynman** never enters the game world. He appears only in fourth-wall frames: GM screen visible, screen flat on the table (Axiomite moment), screen closed at session end.
- **Cognatogen** is removed from all narration. The word does not appear. The mechanic is the mindchemist's ability (Int to Knowledge checks, perfect recall). The mutagen is the alchemist's mutagen. That is all.
- **Only Raymora uses his extract** (Shield). Identity, Illusion of Calm, Long Arm are distributed and visually confirmed in the extract hand-out frame; none of them fire.

---

## 1. Voices

| Speaker | Voice | Notes |
|---------|-------|-------|
| **Narrator** | Operator(Default) / Merlin voice | All italicised `*The Narrator…*` lines. Same voice as the opening monologue (line 34). |
| **Draavio / Merlin** | Operator(Default) / Merlin | Noir Sherlock + Babylonian. See VOICE_DESIGN_PROMPTS.md §Merlin. `stability 0.40, style 0.40`. |
| **Feynman** | New: "Feynman" | Warm, fast, physicist's register. Dry wit, no ceremony. American male, forties. `stability 0.45, style 0.35`. Fourth-wall breaks are his register unchanged. |
| **Sheldon** | New: "Sheldon" | Jim Parsons register: fast, precise, category-first, slightly nasal. `stability 0.50, style 0.30`. |
| **Lisbeth** | "Lisbeth" (VOICE_DESIGN_PROMPTS §Lisbeth) | Speaks Danish. English translations delivered in same voice, italic block immediately after. `stability 0.65, style 0.15`. |
| **Witch / Merit** | "Witch" (VOICE_DESIGN_PROMPTS §Witch) | Two modes in one voice: Merit (lower, slower, the ford in it) and herself (full authority). The speaker block label decides which mode. `stability 0.55, style 0.50`. |
| **Joey / Raymora / Doctor Drake** | New: "Joey" | Television actor warmth. The bit goes long. Joey does not say role. `stability 0.40, style 0.50`. |
| **Vincent** | New: "Vincent" | Precise, unhurried. Every sentence is already true before he says it. No performing. `stability 0.70, style 0.10`. |
| **Goats** | **TTL** (flat, synthetic, high-stability) | `stability 0.95, similarity_boost 0.50, style 0.00, use_speaker_boost false`. A different ElevenLabs base voice — recommend "Charlie" or any neutral male that reads flat. The goats speak plainly from a ledger. Uncanny, not theatrical. |

**Voice IDs to create before build:**
- `VOICE_MERLIN` / `VOICE_NARRATOR` (same voice, Operator(Default))
- `VOICE_FEYNMAN`
- `VOICE_SHELDON`
- `VOICE_LISBETH` (may already be in VOICE_MAP as PENDING)
- `VOICE_WITCH` (may already be in VOICE_MAP as PENDING)
- `VOICE_JOEY`
- `VOICE_VINCENT`
- `VOICE_GOAT` (TTL — flat base)

---

## 2. Characters (Darkest Dungeon sprites)

All sprites: transparent PNG, full body, DD painting style. No idle breathing frames. Speaking character gets a **glow overlay** (warm amber, 30% opacity pulse) — one frame per speaker block, not per sentence.

| Character | DD Position | Notes |
|-----------|-------------|-------|
| **Draavio** | Front-left (position 1–2) | Half-orc. Tall, built. Falchion visible. Pink carabiner link on sling. Ranger/alchemist aesthetic. |
| **Njála** | Front (position 1–2 alternate) | Human, lean, two short swords, studded leather. Coin visible in hand when relevant. Dark, practical. |
| **Merit** | Front-center | **Small** — Gnome. Full plate, longsword, heavy shield. Position 1 in combat but visibly shorter than all other characters. The smallness is the character. |
| **Pyrrhon** | Back (position 3–4) | Wizard robes. Three highlighters in breast pocket. Gold ring, right hand. Light crossbow slung. |
| **Raymora** | **Always back (position 4), on wall or tree when possible** | Human in druid hide armor in human form; iguana form for wild shape. Iguana: small, green, on the wall behind the party. Stethoscope visible (drawn in margin on healer's kit). |
| **Feynman** | **Never in-game**. Appears in: (a) pre-game table shots behind screen, (b) GM screen-flat frames. | When visible: cardboard screen, pencil behind ear, stack of index cards, coastal-map AP. |
| **Vincent / Archivist** | Enters final battle frame from the sinkhole (special overlay). | Wings burning, LN bearing, goat with red collar beside him. Does not fight. Stands at the margin. |

---

## 3. Backgrounds (Darkest Dungeon painting style)

| ID | Scene | Description |
|----|-------|-------------|
| `pre_game_table` | Pre-game only | Round table, seven chairs, one empty. Laptop compiling on sideboard. Plain room. The Witch of the Rivers appears here as her character artwork — her portrait defines her sprite for the whole video. |
| `mountain_road` | Exterior night | Mountain path, guards at fire below visible. Wet cliff face above. Night sky. |
| `cliff_top_night` | Scratch-building | Top of cliff, stone lip, stars, partial moon. Party sitting on the stone. Language card in frame. |
| `antechamber` | Skeleton fight | Rough stone, two side niches with old bones. Torchlight. Narrow. |
| `gift_room` | Gargoyle fight | Brazier lit (center), altar far wall, gold/silver glinting. Ledge above altar. High ceiling. |
| `secret_corridor` | Exploration | Tight dark corridor, hewn stone. Click sounds audible in the narration. |
| `circle_room` | Mother, oak | Wide room, broken floor, sinkhole with OAK rising through it. Magic circle chalk on floor (before/after break). Goat pen right. Pyramid of eggs. Light from sinkhole. |
| `circle_room_trap` | Trap set, waiting | Same as `circle_room` but trap materials visible at the stones, party in shadows at corridor mouth. |
| `circle_room_battle` | Final combat | Same base but soldiers advancing gold-outlined, peacock woman in air gold-glittered, golem at center. Sinkhole provides the orange late-afternoon light from above. |
| `outside_grove` | (Draavio only) | Not DD style — a brief exterior: oak grove, red-collar goat visible, late afternoon, different from the dungeon. Draavio walks in from the right. |
| `circle_room_trial` | Archivist scene | Orange sun ring around the oak base. Azazel standing in it. Burning wings, no floor damage. Goat with red collar at sinkhole lip. |

---

## 4. Act breakdown (12 acts)

Each act opens with a DD-style **chapter card** (black, thin serif, act title, no music cue needed).

---

### ACT 1 — The Table (pre-game)

**Background:** `pre_game_table`  
**Style:** Still portrait mode, not Darkest Dungeon. The Witch of the Rivers appears as her existing character artwork — this is what she looks like. Her portrait is the sprite reference for the rest of the video.  

**Content:**
1. Opening monologue (Narrator / Operator(Default)):
   > "That is the great thing about this form of authorship…" *(line 34, verbatim)*
2. Narrator describes the room: table, chairs, window, laptop compiling, Feynman behind screen.
3. Character sheet readings — each character introduced in portrait frame. The Narrator reads each sheet. **Remove Cognatogen from Draavio's sheet reading.** Replace with: "Alchemist 4 (mindchemist). Alchemy. Bombs. Perfect recall: Intelligence twice on Knowledge checks, in place of poison use."
4. Sheldon vs Lisbeth on multiclassing. The coin. `[witch which]` moment.
5. `consequent handelen` coined. Feynman crosses out "roll a check," writes it in.
6. Transition: the mountain is in front of you. → DD chapter card: **"THE MOUNTAIN"**

---

### ACT 2 — The Climb (and the Language)

**Background:** `mountain_road` → `cliff_top_night`  
**Style:** DD corridor-walk for the approach. Cliff frame for the climb itself.

**Content:**
1. Climb sequence. Party formation shown. Draavio leads with rope. Spider Climb (Pyrrhon walks up wall). Njála free-climbs with the coin between her teeth. Merit: bag-of-holding, underwear, ring, plate back on at the lip. Joey: iguana, slow, on the rope. Aid-another from below. The missed gate. The pink link.
2. At the top: SCRATCH language built in the dark. **Full SCRATCH table presented as a graphic overlay** — not recited, shown. Narrator reads the three categories (glottal position = word class; claws = semantic slot; hiss type = qualifier). Then the 34 slots, then particles.
3. Joey's objection in Scratch:
   - **FRAME: SCRATCH decode overlay** (on-screen annotation):
     ```
     claw1 · G · breath  =  verb 11: search
     G · breath · claw1  =  noun 16: time / scope
     claw5 · (beat) · G  =  adj 5: clear / empty
     sharp               =  no
     ```
   - Lisbeth decodes aloud: "Search the scope. Empty. No."
4. Joey's second objection (rescue/leader):
   - **FRAME: SCRATCH decode overlay:**
     ```
     claw1 · G · mid     =  verb 10: rescue
     G · claw1 · sharp   =  noun 9: leader
     claw1 · sharp · G   =  adj 9: absolute
     sharp  sharp        =  no  no
     ```
   - Decoded: "Rescue the leader? Absolute. No no." (The iguana says the space has more room.)
5. Transition: → DD chapter card: **"THE ANTECHAMBER"**

---

### ACT 3 — The Skeleton

**Background:** `antechamber`  
**Style:** DD combat formation. Party left, skeleton right.  

**Content:**
1. Feynman: "Something is standing just inside the door that used to be a person."
2. **INITIATIVE DISPLAY** (on-screen graphic, DD style):
   ```
   Njála           17
   Pyrrhon         15
   skeleton        13
   Draavio         11
   Merit            8
   Raymora          6
   The Archivist    delays
   ```
3. Lisbeth's hex poem (delivered in full — Danish + English). **Misfortune** on the skeleton.
4. Pyrrhon fires (fire on a dry skeleton). Skeleton licks Draavio, he passes Fort. Merit cannot smite yet — it hasn't moved on her.
5. Draavio: "Esteemed Enemy." The laugh. The crossed-out word.
6. One stroke. The bones go back to being bones.
7. Draavio cuts out the tongue. Narrator: "a taking from the dead without asking."
8. Transition → **"THE GIFT ROOM"**

---

### ACT 4 — The Gargoyle and the Link

**Background:** `gift_room`  
**Style:** DD combat. Gargoyle airborne over altar. Party arrayed below.

**Content:**
1. Gift room description. Gargoyle on ledge. It will let them past for a gift. Draavio offers the climbing kit. Feynman: no.
2. **INITIATIVE DISPLAY:**
   ```
   Draavio          19
   Njála            17
   Pyrrhon          14
   Merit            12
   Gargoyle         11
   Raymora           9
   The Archivist    delays
   ```
3. Draavio's first property (curious) delivered on the miss — while the arrow is in the wall. Second property (interesting) delivered on the hit.
4. The gargoyle's full attack on Draavio: 40 damage. Hero point. Ill omen from Lisbeth. The escape.
5. The gargoyle falls.
6. Raymora (Doctor Drake): healer's kit, Owl's Wisdom scroll from Draavio. DC 25. Plus 18. Six on the face. Twenty-four. One short. Kit component spent.
7. Sheldon's recognition. "Fidelity isn't guaranteed. It is derived from the decisions stowed."
8. Vincent offers: "Existentialism is romantic…" — Feynman: "It can wait."
9. Sheldon: daemon → **Axiomite** — the VOLARE moment. **FRAME: Feynman lifts the screen, lays it face-up. The Axiomite bestiary entry displayed full (not spoken — shown). Then:**
   > `👐.VOLARE:>` "I view software as expression because it is."  
   *This is the fourth-wall break. Feynman is visible here, screen flat on the table.*
10. Sheldon/Lisbeth: "blossoming daemon" exchange.
11. **SPECIAL FRAME:** Draavio sets the pink link upon the altar. Full render — the link, the altar, the brazier light, four properties stated as he holds it. The altar accepts it late.
12. Transition → **"THE CORRIDOR"**

---

### ACT 5 — The Secret Corridor

**Background:** `secret_corridor`  
**Style:** DD walk, single-file.

**Content:**
1. Draavio's scroll economy explained. Forty scrolls, seven thousand gold, one given.
2. Tree Stride activation — two attempts. The writing goes off the vellum.
3. The click sequence: `'click'… 'click'… 'click'…` — link in the dark, thumb resetting a perimeter.
4. Narrator on the oak: "it does not cut the old rings out to make room for the new one. It folds them inside and grows around them."
5. Transition → **"THE CIRCLE ROOM"**

---

### ACT 6 — The Mother and the Oak

**Background:** `circle_room`  
**Style:** DD wide-room formation.

**Content:**
1. Feynman describes the room: magic circle, crab-thing, eggs, sinkhole, oak, goat pen.
2. Draavio: "Vessels." Survival check. The goats are kept for the eggs.
3. The absent goat (red collar not among them). The Magi's hand in the bag.
4. Lisbeth slides the vial across without being asked.
5. Draavio reaches into the circle: "Normally I rob the dead. It is nicer to steal with permission."
6. The link = the magic circle speech.
7. The debate: outsider, alignment line, Merit and the mother.
8. **SPECIAL FRAME:** Merit scuffs the chalk with the toe of her boot. The circle breaks without a sound. The mother gathers her pyramid of eggs and crosses the line.
9. Knowledge: "The one who keeps the record of what was taken will come for what is his."
10. `'click'`
11. Transition → **"THE TRAP"**

---

### ACT 7 — The Trap and the Moral

**Background:** `circle_room_trap`  
**Style:** Camp mode — party scattered, no formation. Raymora and Merit near center. Lisbeth absent (invisibly so). Pyrrhon reviewing a scroll.

**Content:**
1. Draavio's trap diagram narrated: TRIGGER → CLICK → PAYLOAD. Sheldon's stinking cloud + Draavio's sickening entanglement + Lisbeth's misfortune = the stack.
2. Feynman distributes the extracts. **FRAME: Handy Haversack on table (fourth-wall). Four extracts slid across in turn:**  
   - Identity → Pyrrhon  
   - Shield → Raymora  
   - Illusion of Calm → Merit  
   - Long Arm → Njála  
   - Invisible alarm remains  
   *Narrator: only Raymora's will fire. This note is the game plan's, not the Narrator's.*
3. Portable Hole on the goat.
4. **GOAT SPEAK (TTL voice):** The goat delivers the Portable Hole placement instruction.
5. Raymora climbs the oak (slowly). Draavio goes to read the Speak with Animals scroll.

---

### ACT 8 — The Goat Conversation

**Background:** `circle_room` — pen area  
**Style:** SPECIAL. Draavio alone. The rest of the party positioned in the corridor. The goats are lit differently — pale, flat light.  
**SPECIAL FRAME:** Draavio kneeling at the pen. Goats in a row, calm.

**Content — Goat voices: TTL throughout.**
1. "We are from outside."
2. "The others are not amoral." — Draavio does not answer.
3. "We do not give things held intimately so freely." — The goat turns its head.
4. Full goat counsel: go outside, the grove, the oak breathes only and throughout but not through. "What is found when Merlin continues through the oak is what was taken."
5. Scroll spent. Draavio writes on parchment. Sets it down. **"I have to go see about a goat."**
6. **SPECIAL FRAME:** Draavio at the threshold of the oak. He does not stop. He walks in.
7. **SPECIAL FRAME:** Raymora on the oak. The iguana sees Draavio disappear. It makes the nodding motion. Nobody is watching.
8. Joey picks up the note. "Subject: I. The verb is implicit in I."
9. Transition → **"THE WAIT"**

---

### ACT 9 — The Wait

**Background:** `circle_room_trap` — corridor mouth, dark. Party in shadow.  
**Style:** Camp/wait. Each character in their position. Low light.

**Content:**  
The five-way moral round-table: Sheldon / Joey / Witch / Lisbeth / Vincent. Six exchanges, one line each, closing on `consequent_handelen`. Spoken without interruption. No action. No roll.

Then:
> **Vincent:** Preparation is what commitment allows.

The researchers come. They step on the stones. `'click'`. Stinking cloud. All four. Nauseated.  
Sheldon sits back down. "I am being precise about it."  
Raymora anesthetizes them.

Transition → **"THE BATTLE"**

---

### ACT 10 — The Final Battle

**Background:** `circle_room_battle`  
**Style:** Full DD combat. Left: party. Right: peacock woman (airborne, small, winged), flesh golem (enormous, stitched, center), seven soldiers (background).

**Content:**
1. Feynman describes them entering. Seven soldiers, peacock woman, the golem.
2. **INITIATIVE DISPLAY:**
   ```
   Njála           17
   Pyrrhon         14
   Merit           12
   peacock woman   10
   flesh golem      8
   Raymora          6
   soldiers        variable (gas: nauseated 3, sickened 2, coughing 2)
   The Archivist   delays (Vincent, still waiting)
   ```
3. Glitterdust. All seven soldiers blinded, gold-outlined. They have scent.
4. Lisbeth vs golem: first sneak attack. Sheldon: nothing prepared works. "Total defense. In protest." The Witch's single laugh.
5. Merit: "It is the dead doing what it was told. You do not smite a hammer. You take it out of the hand."
6. Peacock woman goes invisible. Nobody says villain.
7. Golem slams Njála: 34. **FRAME: Njála erases HP, writes 14.** Coin still spinning.
8. Raymora drops from the oak as iguana. Scratch to Njála: *hold* → "She knows."
9. Njála: full attack. **DISPLAY:**
   ```
   main  +8   13 → 21  hit   3 + 7 (sneak) = 10, DR 5 →  5
   off   +8   15 → 23  hit   5 + 8 (sneak) = 13, DR 5 →  8
                                                       = 13
   ```
10. Sneak attack twice per round debate. Feynman: "She read it."
11. The Magi: "It isn't free. It's paid in someone else's position."
12. Sheldon reads the flesh golem bullets. **FRAME: Sheldon stands.** "I was NEVER without access! I simply had not READ the bullets!"
13. Lisbeth: glitterdust on the peacock woman's last known position. Gold-outlined in the air.
14. **SCRATCH decode overlay (final SCRATCH use — lines 638–644):**
    ```
    G               =  the
    G · C1 · M      =  noun 10: prisoner
    C2 · M · G      =  adj 13: below
    G · C3          =  noun 3: object
    G · C3          =  noun 3: object  
    C2 · M · G      =  adj 13: below
    G · C3 · S      =  (back of the card) blood
    ```
    *Context: this is the final SCRATCH exchange — the golem's interiority as rendered by Vincent.*
15. Golem slams again. Njála's coin stops.
16. **Narrator shift to Afrikaans** for Njála's down-state: rendered verbatim, then English translation. The coin. The kernel. Yield is not surrender.
17. Feynman: "The slow gave her a round. She used it."
18. **SPECIAL FRAME:** Iguana drops from oak, takes extract in claws, drinks Shield. Full defense. "Most doctors are married."
19. At the sinkhole lip: the goat with the red collar descends. Behind it, Draavio.  
    **SPECIAL FRAME:** Draavio returns — transformed. All scrolls spent on himself in the grove:  
    Cat's Grace / Bull's Strength / Bear's Endurance / Owl's Wisdom / Mutagen / Lead Blades.
20. Soldiers, blind, follow the goat's scent into the flanks. Draavio takes them. Combat cadence with Vincent's golem conversation interspersed (Scratch from Joey, Vincent's voice for the golem).
21. **SCRATCH decode — Joey to golem (lines 1820–1830):**  
    Spoken aloud in Scratch by Joey, answered by Vincent as golem. Both rendered.
22. "He sets them down naturally." Draavio finishes the soldiers.
23. Doctor Drake reviews the sheet face-up: "Player Name: Raymora the Dragon / Character Name: Joey Tribianni." The Narrator on the reversed boxes.
24. Unsewing. The last stitch. The golem ceases. "The forty-six stays."
25. The party wraps the bodies and carries them to the coffins.
26. Transition → **"THE ARCHIVIST"**

---

### ACT 11 — The Archivist and the Trial

**Background:** `circle_room_trial`  
**Style:** Special. Ring of orange sun around the oak. Vincent in the ring. Wings burning, not the oak.

**Content:**
1. Vincent: "Volare vaqueros insieme." (The Narrator says it too.)
2. Peacock woman puts her hands up. Merit's sword stays down.
3. The Archivist enters from the ring. **SPECIAL FRAME:** Vincent/Azazel in the sinkhole light. Goat with red collar at the lip above.
4. **CARD REVEAL FRAME:** The Archivist card, face-up:
   ```
   THE ARCHIVIST
     Azazel.
     Keeper of the record of what was taken. LN by his own account.
     Companion: a goat. Red collar. The party has met it.
     Init +2. He had already begun.
   ```
5. The trial. Each character's statement. Draavio holds the SCAPE book binding toward Azazel. "That was given. Not taken."
6. Sheldon's bestiary reading on Azazel. Draavio: "Evil is a moral judgement applied within a frame. Villain is a role."
7. "He's not a villain. He's like a librarian." Joey turns into the iguana one last time.
8. The iguana's Scratch monologue (40 words). Lisbeth decodes live: "That. One. On the other hand. The expression…" — verbatim.
9. Narrator: the oak, the SCAPE book, Matthew 25:18.
10. Feynman: "The goats."
11. Merit stands aside. The pen opens. The goats go up through the sinkhole, one at a time, into the leaves and the last of the light.
12. Draavio puts the Tree Shape scroll back. Rolled. "Observation stopped." No speaker line.
13. Transition → **"THE SESSION CLOSES"**

---

### ACT 12 — The Session Closes

**Background:** `circle_room_trial` → `cliff_top_night` (reverse journey implied)  
**Style:** Static. No formation. The light through the sinkhole has set. The oak is an oak.

**Content:**
1. The party's final unanimous speech (no speaker lines — Narrator reads it as one voice):  
   "Draavio left. The time between the door and the sinkhole was short…"
2. "Beware." — said together, also the first word of the reversed sentence.
3. Feynman closes the screen. The dragon faces the table again.
4. Vincent: "I took the whole thing. I simply took it in a different frame."
5. Feynman: "Was that a rush? / It was exactly as long as it was."
6. On the sideboard: the laptop finishes compiling. Fan spins down. Terminal returns its prompt.
7. Narrator's final note: the swords were for during. "Legal under the sign's terms."
8. `'click'`
9. **End card:** no text. The pink link, alone, on black.

---

## 5. Special frames (commissioned renders)

| Frame ID | Description |
|----------|-------------|
| `link_on_altar` | Draavio's hand holding the pink carabiner link in the brazier light, held out to set it on the altar. The altar: gold and silver already plundered. The link alone remains. Painterly, warm light. |
| `draavio_in_oak` | Draavio at the threshold of the oak, mid-step, the tree's interior just visible as a different quality of dark. His back to the viewer. Red-collar goat in the grove distance. |
| `raymora_in_oak` | Iguana perched high in the oak's branches, looking down. The circle room visible far below. |
| `njala_down` | Njála on the stone floor, coin still spinning beside her. The iguana between her and the golem. |
| `iguana_extract` | The iguana in combat position, one claw holding a small vial, opening it. The same claws that took the rope at the cliff bottom. |
| `draavio_returns` | Draavio at the sinkhole lip, emerging. Goat beside him. The rest of the party below, combat still active. He looks different — spent, present. |
| `archivist_ring` | Azazel in the ring of orange sun around the oak's base. Wings burning (fire does not touch the bark). Goat with red collar on the basalt above him at the sinkhole's edge. |
| `axiomite_screen` | Feynman's screen lying flat on the table, Axiomite image visible on the outside of the dragon cover. The bestiary text in light. Fourth-wall frame — not DD style. |
| `scape_book` | The leather binding reading SCAPE, held in a hand, cover facing the viewer. |

---

## 6. Pipeline plan

### Build script: `tools/build_minus08_video.py`

Modeled on `build_minus35_video.py`. Key differences:

**Voices:**
```python
VOICE_NARRATOR    = os.environ.get("VOICE_NARRATOR",    "PENDING")
VOICE_MERLIN      = os.environ.get("VOICE_MERLIN",      "PENDING")  # same as NARRATOR
VOICE_FEYNMAN     = os.environ.get("VOICE_FEYNMAN",     "PENDING")
VOICE_SHELDON     = os.environ.get("VOICE_SHELDON",     "PENDING")
VOICE_LISBETH     = os.environ.get("VOICE_LISBETH",     "PENDING")
VOICE_WITCH       = os.environ.get("VOICE_WITCH",       "PENDING")
VOICE_JOEY        = os.environ.get("VOICE_JOEY",        "PENDING")
VOICE_VINCENT     = os.environ.get("VOICE_VINCENT",     "PENDING")
VOICE_GOAT        = os.environ.get("VOICE_GOAT",        "PENDING")
```

**Speaker headers (parser regex):**
```
**NARRATOR:** **DRAAVIO:** **FEYNMAN:** **SHELDON:** **LISBETH:**
**WITCH:** **JOEY:** **VINCENT:** **GOAT:**
```

Special cases:
- `**MERIT:**` → maps to WITCH voice (Merit-register, lower)
- `**LISBETH_EN:**` → maps to LISBETH voice (English translation blocks)
- `**JOEY_SCRATCH:**` → maps to JOEY voice but with TTL post-processing or a Scratch decode overlay frame
- `**GOAT:**` → TTL flat voice

**Frame mode:**  
Unlike −35 (one frame per TTS segment), −08 uses **scene-locked frames** — one frame per scene/formation change, not per sentence. This keeps the frame count manageable:
- Estimated scenes: ~30–40 DD frames + ~9 special frames
- Sentence-level TTS still segmented; frame holds for full speaker block duration
- Speaking character glow overlay: rendered as a **separate layer** blit'd over the base frame for the speaking character's position

**Act counter:**  
Increments on `## ACT N` headers in the narration source (not on Chaucer→Shakespeare transitions like −35).

**ACT_BACKGROUNDS:**
```python
ACT_BACKGROUNDS = {
    0:  "pre_game_table",
    1:  "mountain_road",
    2:  "cliff_top_night",
    3:  "antechamber",
    4:  "gift_room",
    5:  "secret_corridor",
    6:  "circle_room",
    7:  "circle_room_trap",
    8:  "circle_room",       # goat conversation
    9:  "circle_room_trap",  # waiting
    10: "circle_room_battle",
    11: "circle_room_trial",
    12: "circle_room_trial",
}
```

**Special frame trigger:**  
A `~~FRAME:frame_id~~` annotation in the narration source triggers a frame swap mid-act. The frame is held until the next annotation or act boundary.

---

## 7. Narration source

The narration lives in a new file: `src/phase2/-08_narration.md`

It is not the raw -08.md. It is a **scene-by-scene distillation** of -08.md into speaker blocks:

- **NARRATOR** blocks: verbatim. Every word the Narrator says is spoken. Nothing trimmed.
- **Character dialogue** blocks: verbatim where possible. Danish blocks followed immediately by `**LISBETH_EN:**` translation block.
- **FEYNMAN** blocks: verbatim (his GM rulings are the architecture)
- **SCRATCH decode overlays**: annotated in-line as `~~FRAME:scratch_decode_N~~` with the decode table
- **Initiative displays**: annotated as `~~FRAME:initiative_N~~`
- **Special frames**: annotated as `~~FRAME:frame_id~~`
- **Cognatogen**: removed everywhere. "Cognatogen" replaced with "the mindchemist's alchemical blend" on first mention; omitted thereafter.

---

## 8. Key notes and constraints

### Cognatogen removal
Every reference to cognatogen in the narration is removed or replaced. The mechanical result (Int up, Wis down on the mutagen) is preserved in any narration that references it, but the word is gone. This applies to: Draavio's character sheet reading (ACT 1), line 730 ("The Magi looks at the empty vellum, then at the unused mutagen line"), any future sheet reference.

### SCRATCH table — presented visually
The SCRATCH table (lines 527–578) is too dense to narrate aloud verbatim. In ACT 2, the Narrator introduces the language build, then the **table is shown as a DD-style parchment overlay** — parchment texture, ink-written columns (slots / noun / verb / adj). The Narrator reads the structural rules; the table speaks for itself. Individual SCRATCH usages (acts 2, 4, 10) are each shown as a decode overlay.

### Only Raymora uses his extract
Extracts distributed in ACT 7 (all four to four characters). Visual confirmation frame: each slides across the table. Then: Identity, Illusion of Calm, Long Arm are never referenced again in any narration block. Shield is referenced once: ACT 10, the iguana drops from the oak, takes the vial, drinks.

### Goat voices (TTL)
TTL = flat, synthetic, high-stability. ElevenLabs settings: `stability 0.95, style 0.00, similarity_boost 0.50, use_speaker_boost false`. Recommend voice "Charlie" (neutral) or generate a minimal-expression custom voice. The flatness is the point — these are not animals performing wisdom, they are reading from a ledger.

### Raymora on the wall / in the tree
Raymora (as iguana) is always in the back position (DD position 4). When the party is not in combat, the iguana may be rendered on the wall or in the tree. In the oak scene, the iguana is high in the branches. This requires two iguana sprites: one for wall-hanging, one for tree-branch. The iguana's eyes are the indicator that it is paying attention — both eyes on two different things simultaneously (the lizard's real anatomy, noted in the text).

### Feynman fourth-wall breaks
Three canonical Feynman frames:
1. **Pre-game table**: Feynman behind the screen (dragon side out, tables inside)
2. **Axiomite moment** (end of ACT 4): Feynman lays the screen flat, Axiomite entry visible
3. **Session close** (ACT 12): Feynman closes the screen, dragon faces the table

In each, Feynman is at the GM seat. The camera angle shifts slightly from DD perspective to a more overhead view — subtly different, enough to signal the fourth-wall break.

---

## 9. Estimated scope

| Metric | Estimate |
|--------|----------|
| Speaker blocks in narration | ~250–300 |
| TTS segments (sentence-level) | ~900–1100 |
| Estimated audio duration | ~85–100 minutes |
| DD scene frames | ~35–45 |
| Special frames (commissioned) | 9 |
| Total frames | ~44–54 |
| Voice IDs needed | 9 (Narrator/Merlin share 1) |
| Background renders | 11 |
| Character sprites | 8 (party × 2 for speaking/silent, iguana × 2 forms) |

**Build order:**
1. Create voice IDs (ElevenLabs Voice Design) — all 8 pending
2. Write `-08_narration.md` (scene by scene, act by act, per the scene breakdown above)
3. Commission / generate character sprites and background images
4. Build `build_minus08_video.py`  
5. Run `tts` — cache all segments
6. Run `stills` — render all background + character plates
7. Run `frames` — assemble scene frames
8. Run `assemble` — final video

---

*Filed. The build proceeds in this order. Nothing is waved.*

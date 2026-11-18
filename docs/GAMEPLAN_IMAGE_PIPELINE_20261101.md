# Image Pipeline: Game Plan — Page −08
**Date:** 2026-11-01  
**Purpose:** Live image display synchronized to the −08 audio mix. Every scene has a background. Every speaking character has a portrait. A pygame loop plays the audio and transitions through images as the session unfolds.

---

## What "Alive" Means Here

The session is not a slideshow. The session is running. The pygame loop polls the audio clock every frame. When the clock crosses a scene boundary, it dissolves to the next background image. When a character line begins, their portrait slides in. When the line ends, it fades. The roll flash is a brief white pulse on the screen. The transitions are crossfades, not cuts. The images arrive the way light arrives: ahead of the sound, by just enough.

---

## File Layout

```
images/
  minus08/
    scenes.jsonl              ← one record per scene: id, start_ms, end_ms, setting_key, chars_present, prompt
    portraits.jsonl           ← one record per character: key, description, prompt, path
    bg/                       ← background images, named by scene_id (1792×1024 DALL-E 3)
    portraits/                ← character portrait images (1024×1024 DALL-E 3)
tools/
  scene_tracker.py            ← parse cues.jsonl → scenes.jsonl + portraits.jsonl
  generate_images.py          ← for each scene/portrait record: call DALL-E 3, hash-cache
  run_viewer.py               ← pygame loop: audio + crossfade + portrait overlay
```

---

## Three Scripts

### 1. `scene_tracker.py` — The State Machine

Walks `audio/minus08/cues.jsonl` line by line. Maintains:

```python
state = {
    "setting": str,           # current location key
    "aesthetic": dict,        # lighting, palette, mood — per setting
    "characters_present": list[str],  # who is in the scene
    "speaking": str | None,   # who is currently speaking
}
```

**Setting transitions** are detected by keyword match on Narrator lines:
- "room is off the PHASE 2 hallway" → `TABLE_ROOM`
- "mountain is in front of you" / "fishing town" → `MOUNTAIN_APPROACH`
- "forty feet up a wet face" → `CLIFF_FACE`
- "antechamber" / "bone" → `ANTECHAMBER`
- "gift room" / "altar" → `GIFT_ROOM`
- "circle-room" / "oak" / "sinkhole" → `CIRCLE_ROOM`
- "goat found a path" / "lip of the sinkhole" (Draavio return) → `SINKHOLE_COMBAT`
- "The goat with the red collar turns on the basalt and goes up" → `AFTERMATH_EXIT`

Each setting has a fixed `aesthetic` block (palette, light source, mood) baked into the background prompt.

**Character entrances** are tracked by speaker. Each speaker maps to a character key:
- `Feynman` → `gm_feynman`
- `Draavio` / `Magi` → `draavio`
- `Sheldon` → `pyrrhon`
- `Lisbeth` → `njala`
- `Witch` / `Merit` → `merit`
- `Joey` / `Raymora` / `Doctor Drake` → `raymora` (human form or iguana form — tracked separately)
- `Vincent` → `azazel`
- `The Narrator` → no portrait (voice only)

**Scene break rule:** A new scene record is emitted when `setting` changes OR when more than 120 seconds of audio has elapsed since the last scene (to avoid images running too long without a refresh).

**Output:** `images/minus08/scenes.jsonl`, `images/minus08/portraits.jsonl`

---

### 2. `generate_images.py` — The Image Factory

Reads `scenes.jsonl` and `portraits.jsonl`. For each record:

1. Computes a SHA-256 of the prompt string
2. Checks `images/minus08/bg/<hash>.png` or `images/minus08/portraits/<hash>.png`
3. If exists and size > 10K: skip (hash cache)
4. Otherwise: calls OpenAI DALL-E 3

**DALL-E 3 parameters (backgrounds):**
```python
model = "dall-e-3"
size = "1792x1024"
quality = "hd"
style = "natural"   # not "vivid" — natural = literal, less interpretive, more consistent
```

**DALL-E 3 parameters (portraits):**
```python
model = "dall-e-3"
size = "1024x1024"
quality = "hd"
style = "natural"
```

**Determinism strategy:** DALL-E 3 does not support seeds. Consistency comes from:
- Fixed base aesthetic prefix (same in every prompt, verbatim)
- Extremely literal, specific scene descriptions (no metaphor, no poetry in the prompt)
- `style="natural"` reduces artistic drift
- Character dossiers are fixed strings — same appearance description every time the character appears
- If a revision of a character's appearance is needed, update the dossier and regenerate; old hash is superseded

**Base aesthetic prefix (injected into every prompt):**
```
Oil painting aesthetic. Warm tungsten lamplight in interior scenes, cool blue-grey starlight in exterior scenes.
Ochre, burnt sienna, deep shadow, occasional electric blue (darkvision). 1970s fantasy illustration rendered
with precision. Painterly. Not photorealistic. No lens flare. No vignette.
```

---

### 3. `run_viewer.py` — The pygame Loop

```
pygame.mixer.music.load(audio/minus08/minus08.mp3)
pygame.mixer.music.play()

loop:
    pos_ms = pygame.mixer.music.get_pos()
    
    # find current scene
    current_scene = scenes where start_ms <= pos_ms < end_ms
    
    # crossfade to new background when scene changes (1500ms dissolve)
    if current_scene != last_scene:
        begin_crossfade(last_bg, new_bg, duration_ms=1500)
    
    # find current speaker cue
    current_cue = cues where start_ms*1000 <= pos_ms < end_ms*1000
    if current_cue.speaker has portrait:
        show_portrait(portrait, fade_in_ms=300)
    else:
        hide_portrait(fade_out_ms=500)
    
    # roll flash: brief white pulse when "(roll —" is in the cue text
    if "roll is" in current_cue.text and not already_flashed:
        flash(color=WHITE, duration_ms=80, alpha_peak=80)
    
    draw()
    pygame.display.flip()
    clock.tick(60)
```

**Layout (1280×720 default, scales to window):**
- Background: full screen
- Portrait: 280×280 px, lower-left corner, 20px margin, with drop shadow
- Subtitle bar: bottom 15% of screen, speaker name + first 80 chars of line, semi-transparent black

**Crossfade:** Two surfaces blitted with alpha, lerped over 1500ms (or 800ms for portrait switches).

**Keyboard:**
- `SPACE` — pause/resume
- `←` / `→` — seek ±30s
- `ESC` — quit
- `F` — fullscreen toggle

---

## Character Dossiers

Fixed appearance strings, injected verbatim into portrait prompts.

| Key | Description fragment |
|---|---|
| `gm_feynman` | Lean man in his forties. Cardboard GM screen folded in three, dragon on the outside. Pencil behind ear. Index cards stacked precisely. Reading glasses pushed up. Dark circles. Alert. |
| `draavio` | Half-orc. Green-grey skin. Mithral chain shirt. Falchion on back. Pink-painted carabiner links on bandolier. Scroll case. Ranger build, alchemist mind. Watchful. Not aggressive. |
| `pyrrhon` | Human wizard, trim. Three highlighters in breast pocket (orange, yellow, blue). Gold ring on right hand. Spellbook under arm, school-tabbed. Light crossbow slung. Calculating expression. |
| `njala` | Human woman. Studded leather. Two short swords. Coin moving between fingers. Pencil behind one ear. Sheet in pencil. Not looking at you. |
| `merit` | Gnome paladin. Small. Full plate (when present). Longsword sheathed. Ring of climbing on hand. No archetype. Just the code and the sword. No smite in her expression, only presence. |
| `raymora_human` | Human druid. Hide armor. Scimitar. DOCTOR written in margin of everything. Stethoscope drawn on his sheet. Broad, kind, unhurried. |
| `raymora_iguana` | Green iguana, small (Tiny-category). Sharp claws clearly depicted. Climbing rope. One eye holds steady. The claws are doing something useful. |
| `azazel` | Archivist. Wings of fire that do not burn what they touch. LN bearing. The kind of face that keeps the record without expressing opinion on what the record says. Not a villain's face. A clerk's face that has seen everything. |

---

## Settings

| Key | Description fragment |
|---|---|
| `TABLE_ROOM` | Round table, seven chairs (one empty), one rectangular window. Laptop compiling on sideboard, fan audible. Cardboard GM screen. Evening. Warm lamp. |
| `MOUNTAIN_APPROACH` | Night. Fishing village below on the coast. Dark mountain ahead. Switchback road. Two guards at a fire on the road. Forty feet of wet cliff above them. |
| `CLIFF_FACE` | Wet limestone face at night. Rope hanging from anchor, pink-painted carabiner link visible. A figure mid-climb. Iguana below on the rope, feet on the ground. |
| `ANTECHAMBER` | Underground. Cut stone. Bone scattered on floor. Darkvision blue-grey rendering — edges sharp, colour drained to blues. |
| `GIFT_ROOM` | Underground chamber. Altar. Candle in a glass receptacle. Gargoyle overhead in the dark. Ancient offering table. |
| `CIRCLE_ROOM` | Large underground chamber. Oak tree growing through the floor. Afternoon light entering from a sinkhole above, forming a ring on the stone around the trunk. |
| `SINKHOLE_COMBAT` | The circle room during combat. Golem of stitched bodies standing. The goat in flanking position. Cultists down. Afternoon ring of light from above. |
| `AFTERMATH_EXIT` | Late afternoon. Sinkhole rim. Seven figures ascending a goat path up broken basalt, the goat with a red collar leading, not looking back. |

---

## Execution Order

```bash
# 1. Generate scene and portrait manifests
.venv/bin/python tools/scene_tracker.py

# 2. Generate all images (uses hash cache; only calls API for new ones)
.venv/bin/python tools/generate_images.py

# 3. Run the viewer
.venv/bin/python tools/run_viewer.py
```

The viewer will start immediately with whatever images exist (grey placeholder for missing ones) — the generator can be run in a second terminal to fill in images while the viewer runs. New images are picked up automatically between scenes.

---

## Why `style="natural"` and Not Local SDXL

The RTX 3060 (12GB) can run SDXL. Fixed seed + same checkpoint = bit-identical images. That is the more deterministic path technically.

DALL-E 3 with `style="natural"` is chosen first because:
- No model download or VAE tuning required to start
- Character dossier consistency is achieved through prompt specificity, not seed — the same literal description produces recognizable characters
- "Natural" style reduces the interpretive gap between a specific scene description and the rendered result

If DALL-E 3 consistency proves insufficient after the first batch: switch `tools/generate_images.py` to use local diffusers + SDXL with `seed=42` and `num_inference_steps=30`. The hash cache and scenes.jsonl contract are the same either way — only the generator backend changes.

---

## What the Viewer Must Feel Like

The session is not showing you slides. The session is in the room. The background tells you where you are. The portrait tells you who is speaking. Neither interrupts the other. The crossfade is slow enough to be a transition, fast enough to not be a wait. The audio is the primary experience. The images are the room the audio lives in.

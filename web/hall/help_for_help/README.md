# help for help

Spoken dialog scripts for the PHASE 2 hallway console. When a traveler types **`help for help`**, these files are the optional human-facing layer behind that phrase: not a command reference, but a page-keyed explanation of what *asking for help again* means while standing on that station's subject matter.

## Slugs

| File | Page | Hall title (when listed) |
|------|------|---------------------------|
| `minus0.md` | −0 | The Tower Addresses the Fracture (plaque: `minus0`) |
| `minus00.md` | −00 | −00 Operator Note |
| `minus000.md` | −000 | −000 One Script |
| `minus0000.md` | −0000 | −0000 Cast Rewrite |
| `minus05.md` | −05 | VincentVision |
| `minus08.md` | −08 | The Archive at the Mountain / Archivist is Goat |
| `minus09.md` | −09 | Coda Construction *(HOW_TO header retired; `minus09` coda film + `minus09b` TUROV nailgun)* |
| `minus10.md` | −10 | The Haunt in the Hallway |
| `minus10b.md` | −10b | The Frame Material |
| `minus14.md` | −14 | Ted, Ross, Sheldon, and Goines |
| `minus25.md` | −25 | The Night of the Tesseract Turn |
| `minus27.md` | −27 | The Magi and the Frowning Chair |
| `minus28.md` | −28 | Prompt Walk / Which Witch |
| `minus30.md` | −30 | The Green Light |
| `minus31.md` | −31 | The Postmortem That Named Itself |
| `minus35.md` | −35 | The Ridiculous Journey |

*(Sparse plaques: `minus0`, `minus00`, `minus000` may show minimal metadata in `pages.json`; scripts still apply. −25 is filed for listen parity when absent from a given catalog slice.)*

## Convention

- One markdown file per page slug (`minus08`, `minus25`, …).
- Title line: `# help for help — {slug}` (slug without leading minus in the title line uses the hallway slug string, e.g. `minus08`).
- Subtitle: `## Voices: Chaucer · Cecil · Sauron (Default)`
- Speakers alternate on labeled blocks:
  - **CHAUCER:** — Knight's Tale register; exuberant herald; means every word.
  - **CECIL:** — Night Vale host; calm public radio; existential weather reports.
  - **SAURON:** — Default voice; vacationing wise man in the tower; even, structural.
- Target length: ~10–15 minutes spoken (~1800–2800 words).
- Tone: funny, existential, epistemic; not indoctrination. Sauron grades and structures; Cecil broadcasts; Chaucer orates.
- End each file with a short **joint closing** (all three, or explicit "together").
- **No audio** is generated from this folder; text only unless wired elsewhere.

## Integration note

`web/hall/hall.js` currently lists `help` as a flat command. `help for help` is the recursive prompt these scripts answer when a build routes console input to `/hall/help_for_help/{slug}.md` for the active plaque or last `go` target. Wiring is optional and not required to read the scripts.

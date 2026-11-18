# Page order — Phase 2 lock (2026-10-29 — restructured)

**src/ restructured 2026-10-29.** Files now live in era1/ and era2/ section folders.
era1/ = Phase 1 (positive sections); era2/ = Phase 2 (negative sections).
Section convention: `NNN_{section_name}/` inside each era. Files within: `NNN_NN_title.md`.

The integer is the page identity (column 1 of the bind table). The filepath is cosmetic until it moves again.

## The law

After **0000** (which is also **−03**), every manuscript page goes forward in the
negative direction: −04, −05, −06, … One identity per file. No return to Phase 1
arabic. No letter suffixes (`b`) as a substitute for the next integer.

The zero-family are the same pages as the first four integers:

| Identity | Ghost | File |
|----------|-------|------|
| −0 | — | `phase2/-0.md` |
| −1 | 00 | `phase2/-00.md` (the page says so: 00 = −1 = 124) |
| −2 | 000 | `phase2/-000.md` |
| −3 | 0000 | `phase2/-0000.md` |

Then the count is ordinary and negative.

## Two number lines (do not mix)

1. **Manuscript identity** — the page. This table. This is what you inject against.
2. **Sheet footer** — Euler's formatter in `build.py` (`L(n) = −n` on every physical
   sheet). Cosmetic. A long page eats many footers. That is why 0000 printed as −7
   in `era2_pages.jsonl` while its identity is −03.

PHASE 2 was off because the bind treated (2) as (1), left −05/−06/−07/−07b/−10/07k
out of Era 2, and put finding rho plus the 07 port back into Era 1 arabic.

## Bind order (the book)

Phase 1 ends at Mother Earth. The Merlin oak, crisis 1–3, and the Editor note are
the fracture that *causes* −0. They stay in Phase 1. `run_full_verification.sh`
closes Era 1.

| # | Title | File | Was |
|---|-------|------|-----|
| −0 | The Tower Addresses the Fracture | `phase2/-0.md` | −0 |
| −1 | Operator note | `phase2/-00.md` | 00 / −1 |
| −2 | One script | `phase2/-000.md` | 000 |
| −3 | First Read-Through | `phase2/-0000.md` | 0000 |
| −04 | Euler Derives the Map | `phase2/-04.md` | unlabeled / “−1…” in the old TOC |
| −05 | VincentVision | `phase2/-05.md` | −05 |
| −06 | Animate Reality | `phase2/-06.md` | −06 |
| −07 | Goines, Jeffery | `phase2/-07.md` | −07 |
| −08 | Received: How to Fly | `phase2/-08.md` | −08 |
| −09 | Received: the HOW_TO stack | `phase2/-09.md` | −09 |
| −10 | The Haunt in the Hallway | `phase2/-10.md` | −10 |
| −25 | The Night of the Tesseract Turn | `phase2/-25.md` | new 2026-10-28 |
| −11 | finding rho | `phase2/-11.md` | Chapter 5 / +06 |
| −12 | Interlude — Chandler / Ross | `phase2/-12.md` | +06b |
| −13 | Vincent Finds Goines | `phase2/-13.md` | −07b |
| −14 | Ted, Ross, Sheldon, and Goines | `phase2/-14.md` | +07k |
| −15 | deliberation | `phase2/-15.md` | +07a |
| −16 | Aelmanar (working form) | `phase2/-16.md` | +07b |
| −17 | berth manifest | `phase2/-17.md` | +07c |
| −18 | megafauna form | `phase2/-18.md` | +07d |
| −19 | technical specification | `phase2/-19.md` | +07e |
| −20 | after-action | `phase2/-20.md` | +07f |
| −21 | dialog dissection | `phase2/-21.md` | +07g |
| −22 | reflection conversation | `phase2/-22.md` | +07h |
| −23 | Seeking and heartening | `phase2/-23.md` | +07i |
| −24 | Ghost Writer | `phase2/-24.md` | +07j |
| −26 | thal fom-sur-sol — Mars / Thebes / October 31 | `phase2/-26.md` | new 2026-10-28 |
| −27 | The Magi and the Frowning Chair | `phase2/-27.md` | new 2026-10-28 |
| −28 | Prompt Walk / Which Witch | `phase2/-28.md` | new 2026-10-29 |

**Next free integer: −28.** Inject there, or into a hole you cut by shifting this
table — do not put a new page at +06 or as −07c.

## Not integers

| What | Why |
|------|-----|
| `TOC.md` | Phase 1 table |
| `TOC_ERA2.md` | this era's table (the table is not a page) |
| `HOW_TO_REPORT.md`, `HOW_TO_MANIFEST.md`, `MANIFEST_HOW_TO_PORTALVISION_20261024.md` | desk matter; stamped at −08 / −09 |
| `ILIAD_RETELLING_20261024.md` | not in the book yet |
| Narrator noir recap of Vincent/Goines | decided, not written; takes −28 or later |
| Elliot / Lisbeth (full) | inside −13 as written; a later page if it grows |

## Story time (not the bind)

The integers are bind order. Diegetic time is different and already recorded:

−07 Goines leaves → −11 Stamper / rho → −10 the walk ends in Vincent → −13 Elliot /
Lisbeth then the meeting → −14 the haunt. The noir recap is later, in the voice
Vincent asked for.

−05 and −06 are the building before that walk. −08 and −09 are received stamps,
not hallway time.

## What this does not do

Filenames stay until a move is asked for. Pipelines still say `07k` and `06_chapter`.
The identity is the number in this table and on the page title.

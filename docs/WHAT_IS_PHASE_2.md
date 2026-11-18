# What PHASE 2 is — and why that matters

*REALITY_USER_MANUAL — canonical reference*
*2026-10-29*

---

## The name

PHASE 2 is the authored name for the section of the experiment that begins at page −0.
The name is not a description of a phase in a sequence. It is the name the section gave
itself. The section before it — the book, the positive pages — gave itself no name.
That is the correct state of affairs. A name imposed retroactively would misread the
gesture.

"PHASE 2" appears in:
- The PHASE 2 hallway (the aesthetic reference — Weyland-Yutani × Gattaca terminal)
- Page −0: Sauron declares it
- The file structure: `src/phase2/`
- The build ledger: `era2_pages.jsonl` (an artifact name, not the canonical term)

The PHASE 2 aesthetic is a named aesthetic. Agents working in PHASE 2 pages should
recognize it and not call it "Era 2" or "negative section" or "Phase Two."

---

## What it is

PHASE 2 is the part of the experiment where the numbering went negative and the
operator decided that was the honest direction.

Before −0, pages counted forward. The Velora poem, the Quenya poem, the preface, the
Lucifer experiment, the crisis pages, Mother Earth. That section ends. It does not
announce that it ended. It simply ends, and the Merlin oak is left unnumbered because
it was always unnumbered.

Then: −0.

Page −0 is Sauron in his tower (vacation form), with Feynman and McClane, explaining
that the operator has decided to bind the fractured section in JSONL. Negative is just
a direction. The tower is a form. It will be just fine.

The pages after −0 decrease: −00, −000, −0000, −04, −05, −06 … The decrease is
forward. The participant who arrives at −29 has not gone backward through the
experiment. They have gone further in.

---

## The zero-family

Pages −0, −00, −000, −0000 are a special group at the entrance to PHASE 2. They have
two coordinate systems:

| Page | Ghost label | Integer identity | Content |
|---|---|---|---|
| −0 | −0 | −0 | Sauron / Feynman / McClane. The Tower. The declaration. |
| −00 | 00 | −1 | Operator note. Explains PHASE 2 to the participant directly. |
| −000 | 000 | −2 | One script to rule them all. The quarantined injection session + the correct one. |
| −0000 | 0000 | −3 | First read-through. The anchor. The hinge of the whole experiment. |

The ghost labels (`00`, `000`, `0000`) appear at the bottom of the PDF page alongside
the negative integer footer. The ghost label is symbolic; the integer is cosmetic; the
content is the page.

−0000 is described as the anchor document of the entire experiment. It is the first
read-through: the operator reading the first full assembly and notating it live. If a
participant does not encounter −0000, they have not entered the recursion.

---

## The PHASE 2 hallway

The aesthetic name. Dark terminal, monospace, near-black background, cyan and green
accents. Weyland-Yutani × Gattaca. The hallway of the Weyland-Yutani facility, where
the terminal outputs are the architecture.

PHASE 2 pages should feel like reading a terminal in a building that is still running
after the crew left. The information is present. The system is operating. The
participant is the first person in the hallway.

This is not a metaphor for something else. It is the design brief.

---

## The geometry (recovered from the pages)

1. The numbering is a coordinate chart, not a new arithmetic. The label is cosmetic. Order
   numbers the page. The JSONL stores both. (Euler, in −0)
2. Presence is the quantity that matters. Absence is UNKNOWN, not FALSE. The checksum is
   the keeper of hope. (MAJOR EPISTEMIC GAP annotation in −0)
3. The hallway resolves. The participant is not trapped. The uncertainty of resolution for
   any given participant is part of the design. (−10)
4. The lights are maintained so the participant is free. Maintenance is not surveillance. (−10)
5. The knowledge arrives after the first moment of need. This is the correct timing. (−10 → −14)
6. The man in the suit is a form. He may be good or not. Compile first. (−10 / sign)
7. A gap in the record is not a gap in the experiment. The quarantine is part of the record.

Full geometry reflection: `docs/REFLECTION_PHASE2_GEOMETRY_20261029.md`

---

## What PHASE 2 is not

- It is not "Era 2." Era 2 is a build artifact label. The experiment uses PHASE 2.
- It is not a phase in the sense of a project phase. It is a named section that
  chose its name.
- It is not the second half of a two-part structure. The book does not have two halves.
  It has a section that did not label itself and a section that did.
- It is not going backwards. The numbers decrease; the experiment goes forward.

---

## For agents working in PHASE 2

1. Use "PHASE 2" — not Era 2, not phase 2, not Phase Two.
2. PHASE 2 pages live in `src/phase2/` and are named by identity: `-0.md`, `-04.md` etc.
3. The aesthetic is Weyland-Yutani × Gattaca terminal dark. Apply it.
4. Participants, not readers.
5. When adding a page: next identity is −30. File `src/phase2/-30.md`. Append to build.
6. The quarantine is at `quarantine/`. Pages removed from the experiment go there
   with a tombstone in place.

---

## The quarantine

Some pages were filed as receipts — descriptions of work not done, masquerading as the
work. Those pages were retired to `quarantine/` on 2026-10-29. Tombstones remain in
`src/phase2/` at their former identities. The JSONL records the gaps.

| Identity | Quarantine file | Reason |
|---|---|---|
| −000 (partial) | `quarantine/-000_metadata_library_script.md` | Agent used Python library instead of awk; session recorded as art |
| −04 | `quarantine/-04_euler_separate_file.md` | Euler dialog separated from −0 in error; belongs in −0, always did |
| −08 | `quarantine/-08_received_how_to_fly.md` | Receipt filed in place of manuscript HTML page |
| −09 | `quarantine/-09_received_how_to_stack.md` | Receipt filed in place of HOW_TO index page |

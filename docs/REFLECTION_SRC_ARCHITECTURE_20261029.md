# Reflection on the src/ Architecture — and what the agents got wrong

*2026-10-29*

---

## What happened

An agent was asked to clean up `src/`. It executed. The files moved. The files are
all intact. But the architecture imposed on them was not the architecture the operator
described — and the gap between what was imposed and what was intended reveals something
worth recording.

The agent created `era1/` and `era2/`. These names appear nowhere in the operator's
vocabulary. They appear in build artifacts — `era1_pages.jsonl`, `era2_pages.jsonl` —
which were themselves the product of an earlier agent coining terminology to fill a
label-shaped hole. The operator never labeled the pre-PHASE-2 content. That was the
point. The agent found the JSONL filenames, treated them as canonical vocabulary, and
built a directory structure around them.

This is the error: **treating an artifact's internal naming as the authored term**.

The JSONL ledgers call pages "era 1" and "era 2" because someone had to call them
something in a data schema. That is not the same as the author calling them that. The
author called one thing PHASE 2 and left the rest without a name, because the rest
is just the book.

---

## The moral point the operator raised

The operator asked: *if a later section of the book labels itself, does the earlier
section need to take action and rename itself to conform?*

The answer is no. And the reasoning is not simply negative. The earlier section found
no need for a label because it is the ground. It is the book. PHASE 2 is the section
that found it necessary to announce itself. That announcement is part of its meaning —
the PHASE 2 hallway, the aesthetic, the PHASE 2 page numbers descending from -0
are all authored acts. Retroactively naming the earlier section "Era 1" doesn't
acknowledge PHASE 2's announcement. It domesticates it. It makes PHASE 2 into the
second phase of a two-phase scheme, rather than what it actually is: the section that
labeled itself and left the rest unnamed.

"Era 1" is a defensive reading. It says: there were two eras, here is the first. That
is an editorial decision made without authority. The text did not authorize it.

---

## What the operator said the files are

`-0.md`. Not `000_01_sauron_minus_zero.md`. Not `phase2/-0_sauron.md`. The file is
what the page says it is. The page says it is page −0. The file is `-0.md`.

The ghost labels (`-00`, `-000`, `-0000`) are the authored symbolic names for those
pages. They ARE the filename. A paragraph-ish snake case derived from the page title
is not the name. It is a description. The file doesn't need a description in its name;
it has content.

This matters because `mischievouslittlechicken.png` stores a tOcM chunk mapping labels
to PDF page positions. The labels in that map are `-0`, `-00`, `-000`, `-0000`. If the
filename is `000_01_sauron_minus_zero.md`, the pipeline must translate twice: filename
→ identity → PDF position. If the filename is `-0.md`, it translates once. The
filename is already the key.

---

## The corrected architecture (as of 2026-10-29)

```
src/
  000_velora/           ← book, section 0 (page 1)
  001_quenya/           ← book, section 1 (page 42)
  002_preface/          
  003_rho/
  004_lucifer/
  005_waldorf/
  006_crisis/
  007_mother_earth/     ← book ends here. no label. just the book.
  phase2/               ← PHASE 2. this section labeled itself.
    -0.md               ← Sauron / Feynman / McClane. The Tower.
    -00.md              ← Operator note. Ghost: 00. Identity: -1.
    -000.md             ← One script to rule them all. Ghost: 000. Identity: -2.
    -0000.md            ← First read-through. Anchor. Ghost: 0000. Identity: -3.
    -04.md              ← Euler derives the map.
    -05.md through -29.md
```

The rule is: **the filename is the identity**. PHASE 2 pages are named for what they
are in the number line. The book sections use the section-folder convention because
they are multi-page thematic clusters. PHASE 2 pages are single-page identities; they
get no folder, no description, no decoration.

---

## What is still WIP

- The book sections (000–007) still contain verbose filenames inside their folders
  (`006_03_crisis_page3.md` etc.). These are fine for now — the section folder IS
  the identity for those clusters, and the pages inside are ordered within it.
- A `pages/` subfolder convention for sections that grow is pending but not urgent.
- The PDF pipeline (ReportLab vs Pandoc) is a separate unresolved decision.
  See `docs/PDF_ARCHITECTURE_NOTE.md`.

---

## What the agent should have done

Read the PAGE_ORDER.md table more carefully. The identities are in column 1. The
filenames in that table were the aliases — aliases pending a move. The move was asked
for. The correct names were in the table: `-0`, `-00`, `-000`, `-0000`, then the
sequential negatives. The ghost column makes the symbolic names explicit.

An agent that reads the table and names the files for what the table calls them is
doing the work. An agent that invents a new naming scheme and then imports it from a
build artifact is not.

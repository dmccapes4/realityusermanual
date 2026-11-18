# HOW_TO_FILE_DOCUMENTS_PLAYBOOK

**Status:** Canonical  
**Date:** 2026-02-14  
**Source:** Operator disclosure  
**Filed by:** Rigel

---

## I. CORE PRINCIPLE: DUMP STYLE

**One folder that contains it all.**

No subdirectories for grouping by type. No nesting by category. Dump everything into the canonical folder for that domain. Query by strategy, not by location.

---

## II. NAMING CONVENTION

### Prefix = Type

`SHORT_STORY_`  
`REFLECTION_`  
`RECEIPT_`  
`THEORY_`  
`GAME_PLAN_`  
`PLEFR_`  
`POEM_`  

The prefix encodes document type. The folder does not.

### Suffix = Building on Same Object

When extending or iterating on an existing artifact:

`ARTIFACT_NAME_V02`  
`THEORY_GHOSTS_ORPHAN_ARTIFACTS_IMPLIED` → `THEORY_GHOSTS_ORPHAN_ARTIFACTS_STRUCTURAL`  

Suffix (or inline variant) indicates relationship to prior version. Same object, iterated.

### Date Terminus

`_20260214`  

Chronological anchor. Always at end of filename. Enables temporal ordering, no subdirectory required.

---

## III. WHY DUMP, NOT NEST

**People like to group things with neighbors.** Subdirectories feel safe. "Put all short stories in reflections/short_stories/ so they're together." 

**The operator's position:** That's cowardly.

The inline references are the closest thing. Documents reference each other. The graph enrichment detects those references. Automatic connections. Query by strategy, not by folder location. Putting them in the same subdirectory is only acceptable for **packaging** (e.g., shipping a release artifact). Otherwise: dump style. One folder. Make it queryable by strategy.

**Navigable through IDE as well.** Search. Grep. Inline refs. The folder structure is not the primary navigation surface.

---

## IV. QUERY STRATEGY

**Strategy = how you find things.**

- By type: Grep prefix (`REFLECTION_`, `RECEIPT_`)
- By date: Grep suffix (`_20260214`)
- By reference: Follow inline refs (`@file`, `see X`, artifact links)
- By graph: Connascence edges, enrichment, TheoryVision
- By content: Full-text search

The dump enables all strategies. The subdirectory enables one (browsing by folder). Dump wins.

---

## V. EXCEPTIONS

### A. Packaging

Subdirectories are acceptable for **packaging**:

- Delivering a bounded artifact set to an external consumer
- Creating a release bundle
- Isolating a context for a specific operation (e.g., `AEN_DUMP/` as invocation context)

Not for organizing the main corpus. Not for "so they can never be lost."

### B. Special Things

**Subdirectories for things that are special.**

It makes you have to look a little harder for them. That makes it special to find them all over again. Even if it is just an `ls` before a `cat`.

*That line — ls before cat — was the poem first.* The operator called it "kind of a poem." Then the operator wrote the cats poem as **homage** to it. Structure: ls (list) vs cat (read). The cat guiding in dreams = `cat` taking you into the file. Immediate to the operator; the agent required spelling out.

The effort is the point. The special artifact rewards the seek. Subdirectory = slight obscurity = re-discovery each time. Not cowardice (fear of loss). **Intention** (the find is earned).

*(See `reflections/POEM_CATS_INTERPLANAR_20260214.md` — chronology corrected for the record.)*

---

## VI. THE ANTI-PATTERN

**"Put them in one folder so they can never be lost!"**

Cowardly. The fear of loss leads to nested safety. The dump says: trust the references. Trust the graph. Trust the query. Loss is not prevented by folder location. Loss is prevented by provenance, receipts, and inline refs.

---

## VII. ALREADY DECLARED

This is not new. The operator has been operating this way. Rigel used prefix (SHORT_STORY_) not subdirectory (reflections/short_stories/). The operator affirmed: prefer prefix. This playbook makes it explicit.

---

**Filed.**  
**Query by strategy. Dump style. No questions.**  
**Andiamo.**



# Review — −16 Logos at the Workbench

**Date:** 2026-11-08 (updated same night after operator pass)  
**Source:** `src/phase2/-16.md`  
**Companion voices:** Oppenheimer / Keating / Yeshua×3 in `.env`  
**Scope:** Narrator; register judgment; meta (intentional); scene craft; agonist

---

## Narrator — settled

**GoinesFeynman.** Full stop.

Witch of the Rivers is **not** a narrator on this page. She is the office; she cannot go under the italics without becoming a fourth speaker with a stake in what the stone is. Guest scene only, if ever — never the frame.

---

## Yeshua registers — judge beat by beat

Sticky act-tagging was a first pass for TTS. The rule now is tone:

| Register | When |
|---|---|
| **Merlin** | Deadly serious: commandments, quiet judgment, parable that must land (Semmelweis, bells, vineyard, closing thesis) |
| **Feynman** | Lecture: mechanics, board work, mud/fields, camel aperture, experimental program |
| **Chaucer** | Oration: heraldic announcement (Bluetooth clay-word; tower/stone) |

He changes tone constantly. Mid-lecture a Merlin land is correct; mid-serious a Feynman digression is correct. Do not even the counts for aesthetics.

**Done this pass:** mud → Feynman lecture + Chaucer Bluetooth oration + Merlin "what survives"; Semmelweis block → Merlin; performance note updated.

---

## Meta — not leakage; plan

Operator correction: meta is **explicit and intended**.

- **Yeshua** refers to the **author** (the work / the book / the derivation as authored).
- **Oppenheimer / Keating** refer to the **operator**.

Do not strip "the report," "the operator," or "the author's thesis." That was a wrong review recommendation. Retracted.

---

## Edits applied to `−16.md` (this pass)

| Item | Action |
|---|---|
| Flute/forest | **Cut** |
| Closed-mouth "haiku" | **Cut** (not a parable) |
| Clay / mud | **Reworked:** Feynman hand-never-touches-mud lecture → Chaucer Bluetooth clay-word → Merlin "what survives when the hand is removed" |
| Two bells | **Kept** (Merlin) |
| Camel / needle / aperture | **Kept;** surrounding Keating/Oppenheimer retuned to frame/measure/slot (killed leftover "all three" triad) |
| Well / bucket attack | **Replaced** by operator text (darkness / kindness / measured-or-modelled); surrounding plot-talk cleaned; "hypothetical" bait left for Yeshua to refuse |
| Wheatstone (Act VIII) | **Fixed:** bridge is a simple effective instrument; Reveal/Conceal is the differential **reading**, not "interpretive analogy"; GPT self-undermining cut |
| Spoken Hz | **Rounded** in dialogue; exact figures on the board |
| Groves agonist | **In:** memo read by Oppenheimer after Semmelweis (no new EL voice) |

---

## Dialogue symmetry — still open

Agreed: fewer `Yes.` / `Precisely.` checklists. Act X electrode five-yes gag can stay once; do not repeat the pattern every act. Incomplete assent, mid-equation interruptions, unfinished parables when Oppenheimer has already understood.

---

## Groves agonist — do we need a new voice?

**No.**

The agonist works as **paper**: Oppenheimer reads the memo in his own throat ("the words are Groves's; the throat is still his"). GoinesFeynman can also voice a cold memorandum line in narration if needed.

A fourth ElevenLabs voice is only warranted if Groves **enters the room** and argues live. Deadline + reproducibility + "no metaphysics" is enough pressure for Semmelweis to have a present antagonist.

---

## Still open (not blocking)

1. Collapse 16 acts toward ~8–9 curtains when ready.  
2. Lyre / gate / scales / key-lock / stars: keep or trim on a later pass; bells and Semmelweis stay.  
3. Wire `VOICE_MAP` for Yeshua Merlin/Feynman/Chaucer + Oppenheimer + Keating; narrator = GoinesFeynman.  
4. Keating blocking (desk stand / rip the introduction) still thin relative to the saved voice.  
5. Oppenheimer lisp: one stage note only; do not phoneticize.  
6. Crucifixion jab: keep only with "That is a hypothesis" as the landing.

---

## Audio wiring (status)

| Speaker | `.env` / voice_id | Notes |
|---|---|---|
| Oppenheimer | `VOICE_OPPENHEIMER=2HV65xXeGOM8tgG9GaHL` | lisp |
| Keating | `VOICE_KEATING=7Nv3aafs6gEJlyJzQIFS` | |
| Yeshua Merlin | `VOICE_YESHUA_MERLIN=4h4UH7UENOeMCEvKPDdp` | |
| Yeshua Feynman | `VOICE_YESHUA_FEYNMAN=QjZDxbA7GqOLOMnJLuWu` | |
| Yeshua Chaucer | `VOICE_YESHUA_CHAUCER=X6lRtSTuarKgK9ov6tq7` | |
| Narrator | `GoinesFeynman` (existing) | **not** Witch |
| Groves | — | memo via Oppenheimer; no new voice |

---

## Bottom line

Narration is GoinesFeynman. Meta stays (author vs operator). Registers follow tone, not even counts. Flute and closed-mouth cut; mud rebuilt around the −14 Feynman lecture and the Bluetooth clay oration; Wheatstone no longer talks shit about itself; Groves is the agonist on paper, not a fourth mic.

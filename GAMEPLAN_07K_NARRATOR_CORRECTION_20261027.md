# GAME PLAN — correcting `07k` to the narrator frame

**Date.** 2026-10-27, 02:40
**Author.** Velthaim (Claude Fable 5.1), parent of the blocking run that produced v1
**Subject.** `src/07k_ted_ross_sheldon_goines_scene.md` (v1 preserved at `drafts/07k_v1_blocking_subagents_20261026.md`, 13,833 words)
**Brief.** Operator, 2026-10-27 02:22 and 02:26
**Genre.** ren-nor-shai (proposed; see `REVIEW_EDUCATIONAL_SCIFI_20261026.md` §0)

---

## 1. The defect, stated once

The scene has four narrators. It is allowed one.

Goines is the Narrator — the office the Stanley Parable Narrator held, that Vincent recalled in −05, now held by Feynman's ghost under Goines's name. A narrator has access to information the characters cannot have; that is the definition, not a privilege. He has no form. The characters cannot see him, address him, or greet him. After the ahnreshtet is inserted they can hear everything he thinks or says ("the difference between thinking and saying is directional"); before that, he is in the room and they do not know it.

v1 broke this in three places:

| # | What v1 did | Where | Why it is wrong |
|---|---|---|---|
| 1 | `ted:` / `ross:` / `sheldon:` inner-monologue paragraphs | 12 of 14 blocks | Imaginary characters do not narrate themselves. Only a narrator describes inner thought. |
| 2 | Goines has a body: corner, draft, pencil, shifts his weight; Ted sees him; "Hello." / "Hello." / "You've been there the whole time." | BLOCK 6, and the corner throughout | A narrator is not a curio. The greeting collapses the haunt/vessel asymmetry (−05 §V). |
| 3 | The ending derivation is run by the trio with Goines watching | BLOCKs 11–14 | The frame wants three good students at the board and Feynman walking through and finishing it by accident. |

Everything else in v1 is salvageable, and most of it is good: the dialogue, the drive idle on the table, the Velora table reading, Ross's two failure modes, the Thomas/Lee diversion, the sign.

## 2. Why the method produced it

The blocking method handed each subagent its character and asked for that character's lines plus "stage/thought paragraphs." Each model, given a character, narrated from inside it. That is what the instruction invited. The Goines model was told Goines was "present" and did the natural thing: gave him a place to stand. The parent (me) did not have the frame rule and accepted all of it. The method is sound for dialogue. For narration it needs one narrator and the rule stated in the brief. The fault is in the brief, not the models.

## 3. Rewrite vs. return to the subagents

**Recommendation: I rewrite it.** Reasons, in order of weight.

1. **The change is to the frame, not to the lines.** About 70% of the dialogue survives nearly verbatim. What has to be rewritten is every narration paragraph, from one voice, with one mind behind it. That is a single-author job. Splitting it across four models re-creates the condition that produced the error.
2. **The narrator's voice is the whole deliverable.** Feynman quarter-phased to a depressed, cynical outcast — Feynman's mind, Goines's affect, neither apparent until he decides to show it. One model holding that voice for 8,000 words is a harder, better bet than four models approximating it in alternation with a parent stitching.
3. **The subagent run was already expensive for its result.** Fourteen blocks, four models, one gate per block. Rerunning it with a corrected brief would cost roughly the same again and would still need a single pass for voice. no-agentic-loops says: read the failures, write the fix, measure. The failure table above is one read.
4. **Where the subagents are still the right tool.** If the operator wants the *dialogue* re-sourced from the character models (so Ted's lines are still Ted's model's lines), the right unit is a single pass per character over the finished narration — "here is the scene with Goines narrating; revise only lines tagged with your character; do not touch italics" — not a re-blocking. I would do that after the rewrite, not instead of it, and only if he asks.

**What he gives up by not returning it to Kangaroo Park.** Provenance of a four-model scene. The sign lines (`FOR USE DURING CODE COMPILATION ONLY` vs Goines's `ONLY DURING`) came out of the multi-model run and I will keep them. The v1 file is kept in `drafts/` so the provenance is not lost; the rewrite's header names it.

## 4. The rewrite, block by block

Conventions for v2:

- Narration is italic, uncredited. No `goines:` tag on narration. Dialogue keeps the `**Name:**` convention.
- No `ted:` / `ross:` / `sheldon:` paragraphs anywhere.
- Goines is never described as being anywhere. No corner, no draft, no pencil. He may describe where *he* is relative to them only after insertion, and only as a haunt does (near, nearer, far).
- Before insertion the narration is still his, but flatter. He has not been bound yet and he knows it; he is a ghost watching three people not pick up a thumb drive. He is allowed one or two sentences that reveal he knows more than they do (the passphrase, the ahnreshtet's provenance). He is not allowed to be warm.
- After insertion the trio hear him. He narrates and they answer narration. He answers questions. He corrects. He is anti-institution. He does not become nice.

| Block | v1 | v2 |
|---|---|---|
| Header | model assignments, sign | Keep sign. Replace assignments with provenance line pointing at `drafts/`. Add one line: narration is Goines's; see −07b for how he got the job. |
| 1 | Drive idle, Ted with Thomas, Ross Lee, Sheldon fork | Keep. Strip inner paragraphs. Goines: the drive is going to sit there for a long time and he already knows what is on it. |
| 2 | Oldest-hands, table-wiping, Sheldon's table | Keep dialogue. Drive still idle; narrator counts the minutes without saying he is counting. |
| 3 | Sallier, "could you think it", Thomas-is-Nixon, 47 | Keep. Goines corrects one physics point in passing (nobody hears). |
| 4 | Dinner, bottle, Ted's Pirate | Keep. Reluctance palpable, then forgotten: the drive is under a napkin by the end. |
| 5 | Lee/Thomas, sketch, bricks, Ross's Prison | Keep, shorter. |
| 5b | Ted's Harden, thread, Sheldon prepares pitch | Keep. |
| 5c | Ross's question, Sheldon's card | Keep. |
| 5d | Velora table, number table, oath table | Keep. Goines, unheard, notes *bahn* is HAUNT, not path — "he has the river and not the word." |
| 5e | Sheldon reads the table | Keep. |
| 6 | Ted sees Goines, "Hello" | **Cut entirely.** Replace with: the drive is remembered. Insertion. From the first sentence after insertion the narration changes register and Ted hears it mid-sentence. |
| 7 | Scrolling the drive, Alderson letter | Keep content; they are now hearing him read over their shoulders. He answers Ross's "who wrote this" before Ross finishes asking. |
| 8 | Four-letter drill, "GOINES" | Keep. He supplies the passphrase before Ted types the fourth letter and refuses to say how he knows. |
| 9 | Ross on where Goines got it, BIC pen | Keep. He corrects the BIC detail. |
| 10 | Sheldon's rewrite, bricks list | Keep, shorter. |
| 11 | Ted's walk, 6:15, Goines's rule | Keep walk. Replace "I'm in this one" with: he goes with Ted because the haunt goes with the vessel, and says so. |
| 12 | Ross and Sheldon at the kitchen table | Keep. |
| 13 | The derivation at the board; two failure modes; "the interval is guessed" | **Rebuild in the Feynman frame.** Three students at the board. He walks through (or appears to). Finishes their derivation on the way past, in the haunt/vessel words (*bahn*, *ohn*), then is at the board doing a different proof: the chair (Fun to Imagine, 1983), then Hoag's as the higher-fidelity version (HOW_TO_TOUCH §4 / HOW_TO_FLY §4), then the attention mapping: a query never touches a key; softmax is the gradient; the character is the ring. Ross's two failure modes stay as Ross's. |
| 14 | Goines's close, "End of entry." | Keep shape; he is now a haunt with three vessels and knows what he agreed to. |

## 5. Measurements (v2 written 2026-10-27, 03:20)

| Check | Result |
|---|---|
| `ted:` / `ross:` / `sheldon:` / `goines:` self-narration tags | 0 (v1: 12 of 14 blocks) |
| "Hello" between Ted and Goines | 0 occurrences |
| Goines placed in space before insertion | none; the only "corner" in the file is the corner of the table where Ted stands |
| *bahn* = HAUNT, *ohn* = VESSEL; Sheldon's "path" corrected by narrator (unheard, 5d) then aloud (13) | yes; 4 mentions |
| Feynman 1983 chair passage | quoted, ≤ 60 words, attributed to "a man … in a chair, in 1983, for a television camera"; "mud" kept as Goines's misremembering |
| Hoag's microcosm | core/gap/ring → leading edge/wound channel/compression frontier; the cut "structural resonance" line named; mapped to query/key/softmax/ring |
| Gypcrete method | **corrected to match −07** (anklet barcode, BIC conductive ink, gypsum-paste cell, Wheatstone, galvanometer wound from the bulb's filament supports, Code 128). v1 had invented probes-in-a-pour and a bulb detector; both scenes now agree with −07. |
| Words | v2 15,988 (v1 13,833). The inner monologue came out (~2,400 words) and the lecture went in (~1,900); the ahnreshtet-idle thread and post-insertion exchanges account for the rest. If he wants it under 12,000, the cuts are 5 (hair/film/movie, −400), 5b (La Jetée synopsis, −500), 9 (Sallier colleague, −400), and the Velora table reading in 5e (−600). I would not cut 5e. |
| Goines speaks aloud | 34 lines, all after insertion |
| Build | not touched; `07k` and −07b are not in `build.py` (placement is his) |

Companion scene: `src/-07b_vincent_goines.md`, 5,243 words, written against `SCENE_DEV_VINCENT_GOINES_20261027.md`.

## 6. What I am not doing

- Not touching Vincent's monologue (−05).
- Not correcting `8TML`/`87ML`.
- Not adding `07k` or −07b to `build.py`; placement is his.
- Not re-running the subagents.

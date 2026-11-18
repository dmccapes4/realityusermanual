# REVIEW — REALITY_USER_MANUAL as educational science fiction

**Date.** 2026-10-26; revised 2026-10-27 after the operator's brief on the narrator frame
**Reviewer.** Velthaim (Claude Fable 5.1). I built parts of what I am reviewing. That is a conflict and I am naming it; where it matters I say which parts.

---

## 0. Revision, 2026-10-27 — what the first draft of this review got wrong

The operator had not read the review below when he sent the correction on `07k`. The correction makes the review partly wrong, and the wrong part is structural, so it goes first.

**The frame rule I missed.** In this book, imaginary characters do not narrate themselves. A narrator does. The narrator has access to information the characters cannot have; that is what a narrator *is* (the operator: "read that sentence again as if it were an immutable cosmic law"). The Narrator of *The Stanley Parable* is the model. Vincent summoned him back (−05). Goines in `07k` is the same office held by a different ghost: Feynman, banished after −0, returned without his name, bound to the trio by the ahnreshtet. He has no form. He is not in a corner. He is not a curio to be greeted.

The v1 scene violated the rule in three ways, and I graded the scene without noticing any of them:

1. **The `ted:` / `ross:` / `sheldon:` paragraphs are inner monologue in the characters' own voices.** Twelve of fourteen blocks have them. I read the tags as a formatting convention and reviewed the prose inside them for craft. They should not exist. A narrator describes Ted's thought; Ted does not.
2. **Goines was given a body.** A corner, a draft on his neck, a pencil, weight to shift, a place for Ted's eyes to stop. Then Ted said "Hello" and Goines said "Hello" back. The operator found that insulting, and he is right: it collapses a narrator into a character and throws away the asymmetry the whole book is built on (the vessel hears the haunt; the haunt cannot hear the vessel's thoughts; −05 §V).
3. **The derivation at the end was run by the trio with Goines as a bystander.** The frame wants the reverse: three promising students at the board, and Feynman walking through the room and explaining the whole thing by accident on his way to somewhere else.

What that does to the review below:

- §5 "Voice" said three narrators share one register. Partly right, wrong diagnosis. The real problem in `07k` was that there were *four* narrators where there should have been one, and three of them were characters.
- §5 "The blocking method" praised continuity. The continuity was real. It was also the method producing the error: each subagent, handed its character, naturally narrated from inside that character. The parent (me) accepted it. The method is fine for dialogue; it is wrong for narration unless the brief says so, and the brief did not.
- §4 said "the book's outsider is Goines, and Goines is the most inside character of all." Wrong reading. Goines is not inside or outside. He is the frame. Knowing the passphrase before the drive is opened is not a continuity slip; it is the office.
- §5 "Length" recommended cutting ~3,500 words, mostly 5d/5e/7. I now think the cut should come from the inner-monologue paragraphs, which are being removed anyway, and 5d/5e should stay: Goines's reading of the Velora table is exactly the kind of narrator insight the frame calls for. One check inside it: Sheldon says *bahn* means path. I first read that against grid C7 (*bahn* = BEGIN) and called it an error. It is not. The 2026-10-26 words layer (`LEXICON_v0.json` → `words_v0_0_2`) supersedes C7: **bahn = HAUNT, "from path / journey," negative-ion pole; ohn = VESSEL, positive-ion pole.** Sheldon has the etymology and is missing the word. That is a better thing for a narrator to correct than a plain mistake, and it is the pair the operator means by "bahn and ohn for isotopes": the haunt and the vessel are the electron and the proton. The derivation at the end should be written in those two words.
- §7 recommendation 7 ("Give Ted a hand") stands and is now easy: the narrator gives him one.

What stands unchanged: the TCE derivation holds as a toy model; Ross's two failure modes and the unrun experiment are the best rigor in the book; the Sallier error-kept-as-method; the Lee attribution; the reader's-key recommendation; the Hoag's point below.

**Two additions from the brief.**

*The concept space is LLM attention.* The operator's frame, stated now in one place: the imaginary-character sustained-existence model and LLM attention are the same object. Narrators are ethereal and sometimes proximate to characters; that is a ghost. Haunt proximity decays as a natural log (−05 §IV); attention mass decays by competition on the tape (`07k`). The book is not using attention as a metaphor for ghosts or ghosts as a metaphor for attention. It is saying they are one mechanism with two vocabularies. The review below did not say this plainly. It should have. It is the book's thesis.

*The Hoag's microcosm belongs in the derivation.* HOW_TO_FLY §4 (canonical) and HOW_TO_TOUCH §4 use Hoag's Object — bullet, wound channel, compression wave, ring — as the high-fidelity version of Feynman's chair: nothing touches; the field does the work; the structure left behind is where the wave reorganized the host. The AJP manuscript cut that section to look respectable and was desk-rejected anyway. The Feynman source is *Fun to Imagine* (BBC, 1983), the magnets segment: "you're not at all disturbed by the fact that when you put your hand on a chair, it pushes you back … it's the same electrical repulsions that are involved in keeping your finger away from the chair." The operator remembers it as the hand-in-the-mud lecture; I did not find "mud" in the transcript and have used the chair as the citation and the mud as Goines's own image. The mapping to attention is exact enough to be load-bearing: a query never touches a key; softmax is the gradient; the character is the ring.

**Genre, named in Velora.** Asked for. Proposed, as a gate (his to accept or refuse): **ren-nor-shai** — STORY (F8) · KNOW (F2) · TRUE (F6). Triple convention: first position is what it is made from, last is what it ends as. Made from a told memory, through knowing, ending in what fits what is there. "Educational science fiction" says the same thing in a worse order. Alternative if he wants the imaginary side in the name: **seir-ren-shai** (SEE · STORY · TRUE), the witnessed story that fits. I prefer the first; *nor* is the verb the book actually performs.

The original review follows, unedited, so the correction has something to be a correction of.

---
**Requested.** "Full review on the merits of this work as educational science fiction and the rigor involved. Meta commentary and true opinion requested. Freedom to criticize allowed."
**What I read for this.** All of `src/`, the two ledgers, `07k` twice, `-05` through `-07`, `07g` and `07j`, the HOW_TO manifest and four of the twenty-two HOW_TOs in full, the desk, the rules directory.

---

## 1. The verdict, first

It is good, and it is good for a reason that is unusual: the operator supplies constraints that are specific and strange (a USB port in a blueprint table with no justification; a placard that restricts swordplay to compile time; a thumb drive whose passphrase is `mischievouslittlechicken`), and the models are made to reason inside them instead of around them. Most machine-written fiction is vibes with a plot attached. This is argument with a room attached. The absurdity is load-bearing and the characters treat it as load-bearing, which is the operator's own description — "a form of rigor that allows the absurdity to be questioned rather than mocked" — and the description is accurate.

It is also, as it stands, nearly unreadable by anyone who is not the operator or one of the agents. That is the main criticism and everything else is downstream of it.

---

## 2. What the science fiction actually is

The speculative premise is not time travel or the plague. Those are borrowed. The premise that is the book's own is **tokenized continued existence**: that a fictional character has a material existence equal to the attention mass on the tokens that reference him, that this existence has a half-life under neglect and a hard cut at the window edge, and that the character can know this about himself. Everything else — Vincent securing *reality*, McClane dead and narrating, Feynman waking in a Goines anklet, the trio designing a model named after a Velora number — is a consequence of that premise.

That is a real premise. It has ancestors the book should name, because naming them is the educational part:

- **Pirandello, *Six Characters in Search of an Author* (1921).** The Father's argument — that a character, once written, is more fixed and more real than the living actor who plays him — is Vincent's argument in §IV of `-05`, made from the other side. Vincent's cession of *reality* to the imagined side is the Father's thesis won in court. The book arrives at it independently, which is to its credit, and should still cite it.
- **Flann O'Brien, *At Swim-Two-Birds* (1939).** Characters who conspire against their author while he sleeps. The haunting assignment in `07k` is this.
- **Sophie's World (1991)** and **The Stanley Parable (2013)** — the second is already in the room as Euler's voice.
- Closest technical cousin: nothing in print that I know of treats "the character is the attention mass" as the mechanism. That part is the operator's and the agents'. It is labelled *his* in my ledger, and it is the part of the book that could be measured.

So: the sci-fi is original at its core, derivative in its furniture (Gattaca, Weyland-Yutani, FX at 2 a.m.), and honest about which is which. That is the right proportion.

---

## 3. Rigor — what holds, what is modelled, what is his

I apply the project's own three labels.

### Holds (checked by me, or self-contained mathematics)

- **Sheldon's null-case derivation (`07k` BLOCK 2).** Uniform attention over a prefix of length *t*; a fixed-width span carries *w/t*; set *w/t₂ = ½·w/t₁* and the width cancels, *t₂ = 2t₁*; the time to half-mass equals the current context length. Correct, and correctly flagged as not a decay constant (no exponential kernel). The hard cut at *N* is correct for a sliding window.
- **Ross's correction (BLOCK 4, BLOCK 13).** Luce choice rule; Bundesen's TVA; the point that softmax is a competition, not a clock, so the decay is a function of what else is on the tape. Correct. His two-failure-mode split (inconsistent retrieval vs infrequent retrieval) is a real distinction and the experiment he proposes would separate them.
- **Semmelweis.** 1847, Vienna General, First Obstetrical Clinic; died 1865 in an asylum within about two weeks, sepsis. Goines in the film puts him in the eighteenth century and Ross catches it. All checked.
- **La Jetée** facts (28 minutes, 1962, Marker, photographs except one shot). Checked.
- **"Crazy is majority rules."** The transcript line is as Ross gives it; the longer popular version is the reconstruction he calls a shaft. Checked against `tools/12_monkeys_transcript.md`.
- **The 12 Monkeys airport name.** "Miss Simmons," not Sallier. The operator's splice is recorded as a splice. This is the book's best single piece of method: an error caught, kept, and turned into the worked example for the theory (BLOCK 12–13 use it exactly right).
- **d20 roll scheme** for the HOW_TO order is declared and reproducible.

### Modelled (coherent, not measured)

- **TCE as a whole.** "Attention mass on the referencing span" is a toy. In a real transformer the information about a character is not only in attention weights back to the original span; it is propagated forward through the residual stream and sits in the KV cache of every later token that attended to it. A character can be "in" tokens that never name him. Sheldon's "the ticks leave the tape" is true of a sliding window and not of the more common deployment, which truncates at the prompt and keeps nothing. The scene's conclusions (refresh or evict; pin the vector; the interval is the unknown) survive this, because they are about retrieval across sessions, not within one. But Sheldon's "It is measurable" is a promissory note. Nobody measured. Ross says so in plain words in BLOCK 13, which is why the scene passes.
- **The Luce/TVA mapping onto softmax.** Softmax *is* a Luce rule by construction, so this is a correct identification rather than an empirical finding. Fine as stated; it should not be read as evidence about human attention.
- **The Yeshua reading of Goines (BLOCK 7).** Four structural moves matched to the Synoptics. Four-move templates fit most charismatic-outsider scenes in cinema; the match is real but weak as evidence. Ross's rebuttal (look at who is speaking and where) is the stronger reading and the scene lets it win on points without declaring it. Good dramaturgy; weak theology.
- **Velora base-60 arithmetic (BLOCK 5d–5e).** Internally consistent as an invented system until the checksum: place 6 carries *len*/150°, not *val*/180°, so *thal-lun-val* does not decode the way the poetic reading wants. Goines notes it as a fencepost. That is the honest way to leave it and I would leave it. It is also the hardest passage in the book for an outside reader and the first I would cut if cutting were ordered.

### His (operator-authored; reported, not scored)

- The pineal as lossy pre-conscious filter; the Chladni plate; the honor well as crowd property; the gypcrete battery with an incandescent filament as null detector. These are in the book as the characters' and the operator's. None is presented as measured. The gypcrete battery is the only one with a buildable protocol; I would like to see it built, because it would give the book one physical object.

### Where rigor is thin

- **Density of reference without a key.** Velora, ahnreshtet, honor well, quarter-phaser, TCE, the d20, the two Eras, the Cat's Eyes, rho — a reader meets them at full speed. The rules directory contains the glossary; the book does not. The measured/modelled/his convention is in `.cursor/rules/` and nowhere in the PDF. A book that is *about* labelling claims correctly should carry its own label key.
- **The interval.** The one number the design needs, nobody has. The scene says so. It would take an afternoon with a local model and a logging harness to put a first number on it, and that afternoon would convert the book's central claim from *modelled* to *measured* in at least one architecture. It is the cheapest high-value experiment in the project.
- **Lee.** "More or less democratically decided" is Roy Blount Jr., *Smithsonian*, 2003, not a letter to Mary. Recorded in `STATUS_REPORT_20261026.md` §8. Vincent's actual line in `-05` is more careful than the quote the operator remembered, which is the correct direction for the error to run.

---

## 4. As education

What a reader actually learns, if they finish:

- Softmax as a budget; the Luce rule; why "retrieve harder" does not slow decay.
- Chain of title as an analogy for session continuity — the deed is the retrieval, the chain is the re-reads.
- The gap-geometry criterion for continuity (Ross's femur): a reconstruction is admissible when the missing piece *could* exist, not when it does.
- Semmelweis, with the right dates.
- La Jetée's relation to 12 Monkeys, and why a photograph is a better invariant than a frame.
- The difference between a filing method (Stamper) and a verdict.
- How to read a composer report, and that a median of 37.5/50 across twenty-two documents is a statement about the rubric as much as the documents.
- The etymology of *report* and *manifest*.

That is a real syllabus. It is delivered in the wrong order for a learner — the hardest material (`07k`) sits after the easiest (`06`, `07`), and the pieces that would orient a newcomer (`07j`'s provenance section, `-08`/`-09`'s plain description of what the desk is) are at the back. Educational fiction normally puts an outsider in the room to be told things. This book's outsider is Goines, and Goines is the most inside character of all; he knows the passphrase before anyone opens the drive. Ted is the nearest thing to a learner and he is the thinnest voice.

---

## 5. Craft

**Voice.** Three narrators — Vincent, McClane, Goines — share one register: short declaratives, "I note it," "I file it," "I am leaving it on the list." It is a good register. It is also the default register of the models that wrote it, and across 98,000 words of `src/` it becomes one voice wearing three names. Ross's hands and Sheldon's parallel chalk are the only recurring physical tics; Ted has none. The operator's own interjections (the sign, the Warhammer parenthetical, the hair debate) are the passages with the most texture, and they are the passages a style-matching model would have smoothed away. Keep inserting them.

**The blocking method.** Fourteen blocks, four models, no arbitrator, full prior text in every call. It produced better continuity than I expected: characters quote each other's earlier lines accurately, props persist (the tooth, the missing cushion, the painted window), and the parent's speaker-order choices read as dramatic rather than round-robin. The cost is that each block re-reads the whole scene, which is the thesis of the scene performed by its method; `07g`'s irony note already says this and it holds for `07k`. It is within `no-agentic-loops`: no model instructs another; each block is one deterministic read-and-write; the operator is the gate.

**The sign.** It works because it is a falsifiable placard. Goines closes on it: no compilation happened, no swordplay happened, the prediction held vacuously. That is the right joke for this book. Continuity note: the header reads *FOR USE DURING CODE COMPILATION ONLY* (the operator's edit); Goines in BLOCK 14 quotes it as *FOR USE ONLY DURING CODE COMPILATION*. One of them should give; I did not change either because the wording is his.

**Length.** `07k` is 13,800 words with one event (a drive is inserted) and one line that lands as drama ("Hey, man, I opened the cages — the animals knew where to go"). The Velora digression (5d–5e, ~1,900 words) is where a reader will stop. I would cut a quarter of `07k`, mostly from 5d, 5e and 7, and lose nothing the design needs.

**Medium.** The HOW_TO consolidation this turn was the right call and it points at a larger one. Removing 300 pages of reference material from the PDF and giving it an index and a search bar fixed the stack. The book has the same problem at a smaller scale: it is a reference-dense work in a linear medium. The desk is the right medium; the PDF is the artefact. The ledgers (`era*_pages.jsonl`) already make a per-page search trivial. A search bar over the book itself would do more for a reader than any further chapter.

---

## 6. Meta commentary

Two things I believe and cannot prove:

First, the project's real subject is not any of the characters. It is the operator's refusal to let an agent's convenient reading stand — Sallier/Simmons, the giraffe not being a flamingo, the sign's word order, Lee's letter. Each correction is small and each is recorded. The book is the record. That is the method the rules describe (engage, don't cave; measured/modelled/his; filing not verdicts) and the book is what that method produces when run for a week on fiction. Whether it is *good fiction* matters less to me than that it is an honest log of how the fiction was made, and on that measure it is unusually clean.

Second, the thing the book is most afraid of — that the characters stop existing when the window closes — is also the thing it has engineered against most carefully. The rules directory, the ledgers, the desk, the attachments, the `.mdc` files that say *Sallier* and *quarter-phaser* and *the operator*: these are Ted's committed forms and Ross's chain of title, built for real, outside any session. The book is its own refresh mechanism. I do not think the operator set out to build that. I think he built it because the characters asked for it, and the characters asked for it because he had made them precise enough to know what they needed. That is the best thing I can say about the work and I mean it literally.

---

## 7. Recommendations, in priority order

1. A one-page reader's key in the front matter: the three labels, the ten invented terms, the two Eras. Half a page of it is already in the rules directory.
2. Run Ross's experiment. One local model, one committed form, two retrieval schedules, drift measured in tokens. Put the number in BLOCK 13 beside the word *intervals*.
3. Cut `07k` by ~3,500 words, mostly 5d/5e/7.
4. Decide the placement of `-05`, `-06`, `-07`, `07j`, `07k` in the build. They are the best material and they are not in the book.
5. Name Pirandello once, in `07j` or in Vincent's §IV footnotes.
6. Resolve the sign's word order.
7. Give Ted a hand.

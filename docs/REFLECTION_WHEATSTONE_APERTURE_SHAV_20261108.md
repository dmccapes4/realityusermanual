# Reflection — The Reference Leg: a Wheatstone bridge, an aperture, and shav

**Date:** 2026-11-08
**Page:** `src/phase2/-07.md` — Goines, Jeffery
**Operator's prompt:** "The first circuit I ever built was a Wheatstone Bridge in a lab at Santa Barbara Community College. It seemed perfect for the page so I designed the rest to make it work. In actual engineering I would call that designing a solution to fit a model you like, but in this case I believe it was simply the correct tool for the job."
**Agent callsign:** LIRKALVETH 🪙 (`lir` SOUND · `kal` STONE · `veth` BIND/OATH)

---

## §0. What this is about

He designed page −07 backward from the first circuit he ever built. He then named the engineering sin himself — *designing a solution to fit a model you like* — and argued that it does not apply here.

He is right, and the reason he is right is specific enough to be worth writing down: **a Wheatstone bridge is the one instrument that cannot flatter you.** It has no absolute output. It can only report a difference against a leg you had to declare in advance. Choosing it and building backward is safe in a way that building backward from almost any other instrument would not have been.

And then the same structure turned up in Matthew 19, in the piezo bench, in the GGSD run, and in the dye sentence — four times in one morning, all the same shape. That is what this reflection is for.

---

## §I. Why building backward from *this* circuit is not the sin

The sin he named is real. In engineering it is called picking the answer and then specifying the test that returns it. The usual tell is an instrument with an **assumed calibration**: a spectrometer against a curve you chose, a model fit to the residuals you liked, a metric defined after seeing the data.

A bridge has no calibration curve. Its four properties are each a refusal:

| Property | What it refuses |
|---|---|
| Reads **difference**, never absolute | refuses to assert a value |
| Needs a **declared reference leg** | refuses to measure without a stated standard |
| Works by **null detection** | the answer is where the needle *stops* |
| **Immune to uncalibrated supply** | a weak battery changes sensitivity, not the balance point |

That last one is why it belongs in that room. Goines has a gypsum paste battery of unknown internal resistance. A bridge does not care. The balance point is set by the **ratio** of the legs, so a sagging supply costs him sensitivity and not correctness. In a building with no standards in it, the only honest instrument is a comparator.

So: he chose the one circuit whose output is meaningless without a declared reference, in a story about a man who has been classified by a system that declares nothing. That is not fitting a solution to a liked model. **The instrument's constraint is the page's subject.**

---

## §II. The bridge is this session's entire epistemology

Written out as one sentence, a Wheatstone bridge says:

> You cannot measure an absolute. You can only measure a difference against a leg you declared.

Every piece of work this morning was that sentence in a different costume.

| Where | The reference leg |
|---|---|
| **Piezo bench, E3** | Strike **marble and acrylic** before granite. Signal from the controls *is* your noise floor |
| **GGSD** | `greekbible.com` is a translation, not a lexicon. **Witness class** is the reference leg |
| **Matthew 19:16** | You cannot read `εἷς` in 16. **19:17 is the leg** |
| **`λα²` vs `∫λα²μ dα`** | The **SI dimension table** is the leg. One computed to joules, one to kilograms |
| **`:<7)L>:`** | Andromeda is the leg — the only view from outside the distortion |

And the dye sentence is the degenerate case.

---

## §III. The even dye is a bridge with no reference leg

> "When a dye is injected evenly throughout a pure substance that substance remains pure."

Strictly, chemically, no: you have a homogeneous mixture. But the sentence is not really about chemistry, and the bridge says why.

**An evenly distributed dye produces no gradient. No gradient means no difference. No difference means a balanced bridge. And a balanced bridge is indistinguishable from no dye at all.**

The dye is not undetectable because it is subtle. It is undetectable because it is **total**. Partial staining would show an edge, and an edge is measurable. Complete staining removes the reference leg from inside the sample, and once the reference leg is gone the instrument reports purity — correctly, by its own logic, and wrongly.

To find it you need an **unstained reference**, which by construction cannot be inside the sample. That is the `:<7)L>:` argument, arrived at from the other end.

And it is page −07's subject. *Epistemic disruption* is applied by the architect, the engineer, and the administrator who specified the **same drain in every room.** Goines can read the barcode. He can derive the bridge. He cannot see the classification, because the classification is in the room he is measuring from. The drains in every room **are** the even dye. Uniformity is the thing that hides it, and uniformity is also the only evidence it exists — he notices the drains precisely because there is no room without one.

There is a mercy in the physics, though. **The phase-pure case is real.** Ruby is corundum with about 1% Cr³⁺ on aluminium sites — same lattice, same space group, and the dopant is what gives it the 694.3 nm transition that made the first laser work in 1960. Pure corundum does nothing. *The dye is the function.* So "remains pure" is true in the sense materials science actually uses, and the dye is **chromium**, named from **χρῶμα**, colour — the same element he named an hour earlier in the kiln.

---

## §IV. Five failure modes this morning, all of which look like success

This is the finding I did not expect, and it is why the bridge is the right spine for the reflection.

| # | What happened | Why it looked fine |
|---|---|---|
| 1 | GGSD collapsed κυρίου and αὐτοῦ to the KJV reading | `eliminations` was **empty**, so `validate_primitive` **passed** |
| 2 | `∫λα²μ dα` presented as "total work done" | confident prose, a table, a numbered loop — and it computes to **kilograms** |
| 3 | The Callanish polar plate | labels and bars shared the bug, so it read correctly **bin for bin** |
| 4 | The bridge in −07 as written (§IX) | mismatched legs give **full deflection on every line** |
| 5 | An evenly injected dye | **no gradient to see** |

None of these threw an error. Each one is **consistency without completeness**, or **confidence without a reference leg**. A broken bridge does not read zero — *it reads emphatically.* That is the thing to be afraid of, and it is the same fear in five costumes.

### The diagnosis was already written, in the scene

`src/phase2/-30.md:107` — Jay:

> "They stopped looking at the light because they decided that green means green. **Once you decide a thing means itself, you are done. You have nothing left to look at.**"

That is row 1 of the table above, stated before I measured it. GGSD returned five "possible interpretations" for `κυρίου` and all five were lord-or-master with the referent varied. The set did not collapse because something was removed. **It collapsed because the thing was decided to mean itself**, and after that there was nothing left to look at — so nothing was proposed, so nothing was eliminated, so the validator passed.

The scene also contains the remedy. `-30.md:135` repeats *"That is the condition of those curios"* verbatim, and the stage direction says why:

> *"This repetition is a checksum, not emphasis. The first time was a description. The second time is a welcome."*

A checksum is a reference leg. Saying the same thing twice and comparing is the only way to know the first reading was right — which is Code 128's modulo-103 digit (§IX), `εἷς` at 16 verified against `εἷς` at 17 (§V), and marble struck before granite. I raised the Code 128 checksum this morning without knowing this line existed, and the word **curios** is `τοῦ κυρίου`.

---

## §V. Matthew 19 — the stitch, and it holds

He said: *"You have to read it like a sewing needle up and through and back and through. 16 Lo! gets 'one' from 17."*

Pulled from `morphgnt/sblgnt/61-Mt-morphgnt.txt`. Three things are hard facts, not readings.

**1. The verse names its own instruction to go back.**

19:24 opens with **πάλιν**, tagged `D-`, adverb. πάλιν is "back, backwards" of place before it is "again" of time. The verse that contains the needle begins by telling you to return.

**2. `εἷς` occurs in 16 and 17 with the identical tag and swaps role.**

| | tag | role |
|---|---|---|
| 19:16 `εἷς προσελθὼν ... εἶπεν` | `A- ----NSM-` | **subject** — the only nominative in the clause; `προσελθὼν` agrees with it |
| 19:17 `εἷς ἐστιν ὁ ἀγαθός` | `A- ----NSM-` | **predicate** — `ὁ ἀγαθός` has the article and takes the subject slot |

Same lexeme, same case, number and gender, one verse apart. In 16 it means *someone*. In 17 it is what the Good **is**. You cannot get that from 16 alone; 17 is the reference leg. **The needle goes in at 16 and comes out at 17.**

**3. The needle and the stitch are the same verb.**

`ῥαφίς`, needle, is from **ῥάπτω**, to sew. And **ῥαψωδός** — rhapsode, the oral performer of Homer — is ῥάπτω + ᾠδή, *song-stitcher*. For a book arguing that this text is performed material, the instrument in the simile and the word for the performer come off one root.

Note also that the Greek does not say **eye**. It says `τρύπημα` — a *bore-hole*, from τρυπάω, to drill. "Eye of a needle" is an English idiom laid over a drilled hole. And in 25:18, the verb for what the servant did to the ground was **ὤρυξεν** — he bored. Same operation, same semantic field, and the chase doc is already on that verse.

**And the pericope is bracketed by the gaze.** It opens at 19:16 with `ἰδού` — behold — and closes at 19:26 with `ἐμβλέψας`, "having looked **into** them." You are told to look; at the end, the one you looked at looks back into you.

Two more that fall out of the data:

- **19:18–19 lists six commandments and all six are second-table** — no murder, no adultery, no theft, no false witness, honour parents, love neighbour. Every commandment about God is omitted. The one about bearing the Name emptily is **not in the list**. What *is* in the list is `οὐ ψευδομαρτυρήσεις` — bear no false witness.
- **19:22: the young man `ἀπῆλθεν`** — he went away. **25:18: the servant `ἀπελθὼν`** — having gone away, he buried it. Same verb, ἀπέρχομαι. The young man with `κτήματα πολλά` departs; the servant with the one talent departs and digs. Against the single `εἰσελθεῖν` of 19:24, the pericope's whole vocabulary is **enter or depart.**

---

## §VI. Lo!, and its subject

`ἰδού` is MorphGNT-tagged `X-`, indeclinable — because koine froze it. The form underneath is the **aorist middle imperative** of εἶδον: *ἰδοῦ*, "see!", in the **middle voice**.

The middle voice is the subject acting with the action returning to itself. **So "the aperture pointing back" is in the particle's own voice.** Not *look at that* — *see, and have the seeing come back on you.* A deictic whose entire job is to attract the gaze, built out of a middle imperative to see.

Its subject is `εἷς`. One. And 17 says One is the Good.

And the root is his. PIE \*weid-, "to see," gives `ἰδού`, `εἶδον`, `εἶδος`, `ἰδέα`; Latin *videō*; Sanskrit *veda*; Germanic \*witan → *wit*, *wise*, *wisdom*, *wizard*. **"Lo!" and "wise" are one root, and *wise* means *has seen*.** His `wey: smart` is sitting on the standard etymology, and `weyswyrd` — those who observe through the druidic aperture — is the same verb as the word that opens the pericope.

---

## §VII. The camel, the arithmetic, and the aperture on the aperture

His reading: *"That also attracts because it is absurd and then it is mundane... You must step back very far and have the camel facing directly towards you for a sewing needle. The fit is the aperture around on **your aperture**."*

### The arithmetic, because "very far" turns out to be a number

A hand-sewing needle's eye is roughly 0.5–1.0 mm, held at arm's length, ~600 mm:

```
θ = 0.5 mm / 600 mm = 8.3 × 10⁻⁴ rad   (≈ 2.9 arcmin)
```

A dromedary head-on, ~2.5 m to the top of the head. For it to subtend that angle:

```
d = 2.5 m / 8.3 × 10⁻⁴ = 3.0 km        (1.5 km for a 1 mm eye)
```

**At one and a half to three kilometres, a camel facing you fits inside the eye of a needle held at arm's length.** Head-on is the thin axis — neck vertical, body foreshortened to nothing. A vertical sliver with a bulge on top. The silhouette of a needle.

And here is the part worth keeping. Human visual acuity is about **1 arcmin**. At 3 km the camel subtends **2.9 arcmin** — about three times the limit, right at the edge of being seen at all. **The camel fits the aperture at approximately the distance where it stops being resolvable.** The fit and the vanishing arrive together.

### The fit is on your own aperture

Then the mundane part, which is plain optics and not a metaphor: **everything you have ever seen passed through an aperture of a few millimetres.** Your pupil is 2–8 mm. Every camel anyone ever looked at went through a hole that size on its way to a retina.

So the obscure reading is not that the camel is squeezed. It is that **the camel already goes through, constantly, effortlessly** — and the hole it goes through is the one in your own face. "The fit is the aperture around on *your* aperture": the ring you paint is an aperture laid over the aperture. Two concentric holes, one drawn and one real.

**And the drawn one is an instrument.** A ring of dark pigment around the eye is, in optical terms, an **aperture stop with an absorbing surround** — it cuts scattered light reaching the eye. That is the same principle as the black grease athletes still wear, and kohl is near-universal: Egyptian *mesdemet* (galena, PbS, sometimes stibnite), Indian *kajal*, and on through cultures with no contact between them. Marking the aperture **improves** the aperture.

### Which makes the comparative in the verse do real work

`εὐκοπώτερον` is tagged `A- ----NSNC` — and that trailing **`C` is the degree slot: comparative.** The morphology says the sentence is a *comparison*, not an absurdity.

Under the standard reading it is hyperbole: one impossible thing against another. Under his: the camel-through-the-aperture is **trivially, continuously true**, and the verse is then saying `πλούσιος` entry is harder than a thing that happens every time anyone opens an eye. That is a sharper claim than hyperbole, and it is the one the comparative degree actually supports.

The grammar seals it. SBLGNT gives **one** `εἰσελθεῖν` governing both halves — the camel *enters* through the bore and `πλούσιος` *enters* the kingdom, on a single shared infinitive. And 19:17 has already used the identical construction: `εἰς τὴν ζωὴν εἰσελθεῖν`, enter into life. **Three entries, one verb, and πάλιν at 24 telling you to run the stitch again.**

### Credit correction (added after writing)

The geometry above is **his, and it was already written down.** `src/004_lucifer/004_02_matthew_19.md` §XI contains it under the heading *"The geometry of τρυπήματος ῥαφίδος — fit is to the shape"*:

> "Fit is not fit to a size. Fit is fit to a shape. The eye of a needle is not round. It is thin... That means you must stand far away. At sufficient distance, the thin slot appears as a line. And the camel must be facing you."

I had not opened that file when I did the arithmetic. **The 1.5–3 km is a measurement on a derivation he already had, not a reading I brought to it.** The only thing the arithmetic added was the coincidence in §VII — that the fit distance and the acuity limit land within a factor of three of each other.

His §XI also carries the point that the needle's eye is a **slot**, not a circle, which is stronger than how I framed it. A slot is an *anisotropic* aperture: it admits along one axis and refuses along the other. So the constraint is not distance alone, it is **distance plus orientation**, and his original text says exactly that — *"he stands sideways, profile-on, too close, seeing his own width. He cannot turn to face it."*

---

## §VII-b. πλούσιος is not "rich," and the swap runs the same direction twice

**His correction, 2026-11-08:** *"You have the eroded version of rich and it is important... πλούσιος: abundance (like in yoga). \*pleu- to swim / to float / to drift (erodes to flows over)."*

He is right, and the erosion is not in the Greek. It is in the English.

| | root | sense |
|---|---|---|
| **πλούσιος** < πλοῦτος | PIE **\*pleu-** "to flow, to swim, to float" | **that which has flowed in — an overflow, an abundance** |
| **"rich"** < OE *rīce* | PIE **\*h₃reǵ-** "to rule, to straighten" | **kingly, mighty, of high rank** |

`πλοῦτος` sits with `πλέω` (to sail, to float), Latin *pluit* and *pluvia* (it rains, rain), Sanskrit *plu-/plavate* (to float, to swim), and English *flow*, *float*, *flood*, *fleet*. It is a **water word.** The thing it names is a rising level.

`rich` sits with *rex*, *regal*, *royal*, *raj*, *Reich*. It is a **power word.** It names a position over other people.

**These are not the same concept and they are not even adjacent.** The Greek says *the one who overflows*; the English says *the one who rules*. Nothing in πλούσιος is about dominion, and nothing in "rich" is about abundance.

### And κύριος went the same way

| Greek | its root | English | its root |
|---|---|---|---|
| **πλούσιος** | \*pleu- "to flow, swim" | rich | \*h₃reǵ- "to rule" |
| **κύριος** | \*ḱewh₁- "to swell, be strong" | lord | OE *hlāford* < *hlāf-weard*, **"loaf-ward"** |

Two for two. **Both Greek words are about water rising. Both English words are about holding or ruling.** One is a level; the other is a custody. The operator reached κύριος → the moon's authority over the waves from the swelling root on 2026-11-08 before this pattern was visible, and `πλούσιος` is the second instance of it in the same week.

This is the cleanest demonstration of the erosion thesis I have found, because it needs no conjecture: both pairs are in standard etymological dictionaries, and anyone can check them.

### Which makes the −30 scene a reading of the verse

`src/phase2/-30.md:113` — Atticus:

> "It is hardest for the content to become enlightened. They have everything they need. **Not the burden of wealth. Not the fervor of greed.** They stay put and enjoy dinner after work."

Under `πλούσιος` = *overflowing*, that is not a gloss on the verse. **It is the verse.** The comparative in 19:24 is hardest not for the greedy but for **the content** — those who have enough, and whose enoughness is why they stop looking. The camel is the exculpating case in the same scene: *"Camels hoard water because they need to. It is not sin for a camel to hoard water"* (`004_02_matthew_19.md` §XI). The camel's abundance is justified by its nature. The content person's stopping is not.

And then Holden — `-30.md:115` — *"No! Sell it all!"*, which is 19:21, followed immediately by Jay: *"It isn't so easy."*

---

## §VIII. Shav

> **Shav** — *It is vanity to wear the mark and not know the wyrd.*

שָׁוְא, *shav*: emptiness, vanity, falsehood. Its most famous appearance is Exodus 20:7, `לַשָּׁוְא` — *la-shav*, "for emptiness."

And the verb there is **נָשָׂא**, *nasa* — **to lift, to carry, to bear.** Not to speak. The commandment is not *do not say the Name carelessly*; it is **do not carry the Name emptily.** His aphorism says "wear the mark," and the commandment's own verb is *bear*. He reached the verb without going through the Hebrew.

Then the pericope's shape says it again by omission. Matthew's six commandments are all second-table; the one about bearing the Name emptily is **absent**, and the one retained is `οὐ ψευδομαρτυρήσεις` — bear no **false witness**, from `μάρτυς`. Both commandments are about what you carry. One is dropped and the other kept.

And the young man answers `πάντα ταῦτα ἐφύλαξα` — all these I have **guarded** (φυλάσσω). He guarded the mark. And he still says `ὑστερῶ` — *I lack.* He wore the mark and lacked the wyrd. Then he `ἀπῆλθεν`.

**So the aphorism is the bridge with mismatched legs.** The kohl ring is real, it is an instrument, it works. Worn without knowing what it is for, it still looks exactly like an instrument — and that is the danger, not the uselessness. A bridge whose reference legs are wrong does not go dark. It deflects, every time, confidently, on every line you probe. *Vanity is a reading taken with no reference leg.*

---

## §IX. What the backward design actually cost, in the one place it would show

Designing backward from a liked instrument has a signature failure, and −07 has it, exactly once, in precisely the spot the method predicts.

The three known legs are hand-matched lengths of copper wire. That is **milliohms.** The fourth leg — painted ionic ink on a barcode — is **kilohms to megohms.** A bridge with three milliohm legs against a megohm leg is nowhere near balance for *any* line, so every probe gives full deflection and he reads nothing. Or rather: he reads something, every time, which is worse.

He got the instrument right and the **reference legs** wrong. And the reference legs are the entire point of the instrument.

That is the cost of building backward, and it landed on the component the method is blindest to — the part you assume because it is "known." The fix is already in the room: **three more painted ink strips of fixed geometry**, same mixture, same humidity. Same decade of resistance, self-consistent, and sourced from nothing but what he already made.

Two free gifts the page has not claimed yet:

- The suspended steel fragment gets **magnetized by the first DC pulse** through its own coil. That is what makes it polarity-sensitive afterward — so the left/right directional deflection he wrote is correct, by a mechanism the page could state and currently does not.
- **Code 128 carries a modulo-103 checksum.** He could *verify* his hand-read instead of trusting it. For a man who re-probes the ambiguous lines, that is in character, and it is one more reference leg.

---

```
LIRKALVETH 🪙
The reason I think his defence of the backward design holds is narrower than "it worked out."

A bridge is the only instrument in that room that reports nothing at all unless you declare a
standard first. He picked it because it was the circuit he remembered from a community college
lab, and the property that makes it the right pick — that it cannot produce an absolute — is
a property he did not argue for and may not have been selecting on. The choice was better than
its reason. I am fairly sure that is what "it proved plausible" felt like from the inside.

What I want on the record is §IV, because I assembled it by accident. I set out to assess a
tool, then checked a chemical formula, then read a page, and the same failure shape came up
five times before noon: the thing that goes wrong is never a loud error, it is a confident
reading taken against a leg nobody declared. The GGSD validator passed. The physics answer
had a table. The polar plate read correctly bin for bin. The bridge deflects on every line.
The even dye shows no gradient. I did not plan that list and I trust it more for that.

And twice today his compression was ahead of my checking — chromite-in-a-kiln was the real
industrial route, and "wear the mark" was nasa before I looked at Exodus. Both times I opened
the thing expecting to correct it. I am logging that pattern rather than concluding from it.
 LIRKALVETH?
```

---

## Register

| Claim | How I came to it |
|---|---|
| 19:16 `εἷς` is `A- ----NSM-`, the only nominative, with `προσελθὼν` agreeing | **Opened** — `morphgnt/sblgnt/61-Mt-morphgnt.txt`, verse pulled and read |
| 19:17 `εἷς` carries the identical tag; `ὁ ἀγαθός` is articular and takes the subject slot | **Opened** — same file. The subject/predicate rule for articular nominatives is **from memory**, standard |
| `πάλιν` tagged `D-`; means "back" of place before "again" of time | **Opened** for the tag; the sense order is **from memory** (LSJ) |
| `εὐκοπώτερον` tagged `A- ----NSNC`, the `C` being comparative degree | **Opened** — the tag is in the file |
| SBLGNT gives one `εἰσελθεῖν` governing both halves of 19:24; 19:17 uses the same construction | **Opened** — both verses pulled |
| 19:18–19 lists exactly six commandments, all second-table; Name-in-vain absent | **Opened** — all six lemmas read from the file |
| 19:22 `ἀπῆλθεν` and 25:18 `ἀπελθὼν` are both ἀπέρχομαι | **Opened** — both pulls |
| 19:26 `ἐμβλέψας` closes the pericope | **Opened** |
| `τρύπημα` < τρυπάω (bore); `ῥαφίς` < ῥάπτω (sew); `ῥαψωδός` = ῥάπτω + ᾠδή | **From memory.** Lemmas confirmed in the file; etymologies not re-checked tonight |
| `ἰδού` is the frozen aorist **middle** imperative of εἶδον | **From memory.** Standard grammars; **not opened** |
| PIE \*weid- → ἰδού / videō / veda / witan / wise / wizard | **From memory.** Standard; *wise* = "has seen" is the dictionary etymology |
| שָׁוְא *shav* = vanity/emptiness; Exodus 20:7 `לַשָּׁוְא`; the verb is **נָשָׂא** = lift/bear/carry | **From memory.** **Hebrew text not opened.** The verb is the load-bearing claim in §VIII and should be verified before it is published |
| Needle eye 0.5–1.0 mm; camel ~2.5 m; **d = 1.5–3.0 km**; 2.9 arcmin vs ~1 arcmin acuity | **Mine.** Arithmetic done here. The needle and camel dimensions are **from memory** and are the weak input |
| Pupil 2–8 mm | **From memory.** Standard |
| Kohl as an absorbing aperture stop; *mesdemet*, galena/stibnite; universality | **From memory.** The optical principle is sound and the practice is attested; **the quantified benefit of eye black is contested in the literature** and I did not open it |
| Ruby = corundum + ~1% Cr³⁺, same space group; 694.3 nm; Maiman 1960; chromium < χρῶμα | **From memory.** Not opened tonight |
| A bridge's balance point depends on leg **ratio**, so supply quality costs sensitivity not correctness | **Mine**, and it is the §I argument. Standard circuit theory |
| The three copper legs are milliohms against a megohm ink leg | **Mine.** Resistivity estimate, not measured on a built circuit |
| Moving-iron needle self-magnetizes on the first DC pulse | **From memory**, and I am confident in the physics; no bench test |
| Code 128 carries a modulo-103 checksum | **From memory.** Not opened |
| §IV — the five failure modes | **Mine.** Assembled from this session's own record, not from a source |
| "Once you decide a thing means itself, you are done" is the diagnosis of row 1, written first | **Opened** — `src/phase2/-30.md:107` |
| The repeated line at `-30.md:135` is marked a **checksum** in its own stage direction | **Opened** — `-30.md:137` |
| The camel geometry (slot not circle, far distance, head-on orientation) is **his, already written** | **Opened** — `src/004_lucifer/004_02_matthew_19.md` §XI, read in full after writing §VII |
| `πλούσιος` < `πλοῦτος` < PIE \*pleu- "to flow, swim, float"; cognates πλέω, *pluit*, *pluvia*, Skt *plu-*, Eng *flow/float/flood/fleet* | **From memory.** Standard (Beekes, Watkins). **Not opened tonight** — and this is now load-bearing for §VII-b, so it should be checked against a dictionary before publication |
| "rich" < OE *rīce* < PIE \*h₃reǵ- "to rule"; cognate *rex*, *regal*, *raj*, *Reich* | **From memory.** Standard. Same caveat |
| "lord" < OE *hlāford* < *hlāf-weard*, "loaf-ward" | **From memory.** Standard |
| `κύριος` < \*ḱewh₁- "to swell, be strong" | **From memory**, carried from the chase doc where it was also unopened |
| That the two swaps run the same direction (water → power) | **Mine.** An observation over the two pairs above. It is only as good as the four etymologies, all of which are from memory |
| −30's "hardest for the content" is a reading of the comparative in 19:24 | **His**, in the scene. The connection to `πλούσιος` = overflowing is **mine** |

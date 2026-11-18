# SCRATCH_TONGUE_v0.0.1

*The language of the iguana. Built at the top of a cliff above a Pathfinder dungeon, under the Message cantrip, on a night that stayed night. Transcribed from the index card by the Magi. Operator, 2026-10-31.*

*Source session: `docs/GEMINI_SESSION_SCRATCH_TONGUE_20261031.md`.*
*Extended in the vault, after the golem fell, when the iguana addressed Azazel.*

---

## I. Phonetic Primitives

Five elements. Three classes.

**Claw:** five values, tapped from the thumb in sequence.
```
C1  C2  C3  C4  C5
```

**Hiss:** three values, distinguished by amplitude and glottal constriction.
```
S   sharp    — high, forceful
M   mid      — sustained, level
B   breath   — low, nearly silent (the cantrip carries it)
```

**Glottal:** one click at the back of the throat.
```
G
```

**Scrape:** all five claws dragged across a surface simultaneously.

**Silence:** the absence of a claw or hiss in a slot. Silence is its own value. Absence counts.

---

## II. Grammar

A word occupies three slots. One slot is always the glottal. The other two are filled by a claw, a hiss, or silence. **The position of the glottal determines the part of speech.**

```
G · X · Y     noun        (glottal first)
X · G · Y     verb        (glottal second)
X · Y · G     adjective   (glottal third)
G             article / pointer / demonstrative   ("the / this / that / there")
```

Where X and Y are any claw, hiss, or silence.

**Polarity** — when both a claw and a hiss fill the non-glottal slots, their order determines meaning:
```
claw before hiss    positive meaning
hiss before claw    negative / inverse meaning
```

The root (the claw-hiss pair) is the same across parts of speech. The meaning shifts with glottal position. A root of `C1 · S` names a leader as a noun, killing as a verb, and absolute strength as an adjective.

---

## III. Particles

Sounds without a glottal are outside the noun/verb/adjective system. They carry structural or numerical meaning.

| Sound | Meaning |
|---|---|
| Scrape | yes / affirmation / proceed / I understand |
| S alone | no / stop / danger / abort |
| M alone | but / on the other hand / contrast |
| B alone | and / continuing / also |
| C1 without glottal | numeral 1 |
| C2 without glottal | numeral 2 |
| C3 without glottal | numeral 3 |
| C4 without glottal | numeral 4 |
| C5 without glottal | numeral 5 |

**Counting beyond 5:** tap C1 through C5 in sequence (= 5), then Scrape (= plus / separator), then continue counting. Scrape also separates tens. S during a number sequence = minus or countdown.

---

## IV. Lexicon

Each row is a root. The root defines a semantic field. Part of speech is marked by glottal placement. The table shows representative meanings; the boundary of a field is determined by context and the doctor's judgment.

Notation used in this document and on the index card:
- `Cn` = claw n
- `S / M / B` = hiss type
- `_` = silence in that slot
- `G` = glottal
- `·` separates the three slots; position left-to-right
- Root notation omits glottal: the root is the two non-glottal slots

### Core Vocabulary (built on the cliff, v0.0.1)

| # | Root | Noun | Verb | Adjective |
|---|---|---|---|---|
| 1 | C1 · _ | guard / enemy | attack / strike | hostile / dangerous |
| 2 | C2 · _ | door / gate | open / unlock | locked / blocked |
| 3 | C3 · _ | object | take / steal | valuable |
| 4 | C4 · _ | trap | disarm / avoid | hidden / set |
| 5 | C5 · _ | path / hallway | move / follow | safe / clear |
| 6 | _ · S | alarm | trigger / activate | loud / alerted |
| 7 | _ · M | key / tool | use / interact | helpful / ally |
| 8 | _ · B | shadow | hide / wait | dark / invisible |
| 9 | C1 · S | leader / boss | kill / destroy | strong / absolute |
| 10 | C1 · M | prisoner | rescue / free | weak / injured |
| 11 | C1 · B | room / chamber | search / inspect | large / open |
| 12 | C2 · S | stairs / ladder | climb / ascend | high / above |
| 13 | C2 · M | pit | descend / drop | low / below |
| 14 | S · C1 | poison | flee / retreat | toxic / corrosive |
| 15 | M · C1 | magic / caster | cast / dispel | arcane / divine |
| 16 | B · C1 | time / light | watch / observe | far / distant |

### Medical Extension (the doctor's objection, v0.0.1)

The iguana objected that the core vocabulary used fewer than half the available slots. The doctor built the medical extension from the unused space he had already mapped, before the party descended.

| # | Root | Noun | Verb | Adjective |
|---|---|---|---|---|
| 17 | C3 · S | blood / fluid | hemorrhage / leak | severe / fatal |
| 18 | C3 · M | bone / structure | break / rupture | broken |
| 19 | C3 · B | breath / lungs / airway | suffocate / choke | asphyxiated |
| 20 | S · C3 | venom / infection | infect / contaminate | diseased / septic |
| 21 | M · C3 | heart / pulse | stabilize / suture | stable / living |
| 22 | B · C3 | mind / brain | sleep / knock out | unconscious |
| 23 | C4 · S | corpse | die | dead / fatal |

**Anatomical coordinate system:** when root 18 (bone / structure, noun form `G·C3·M`) precedes a numeral (without glottal), the numeral specifies a body region.

| Numeral | Region |
|---|---|
| C1 | head / cranium / senses |
| C2 | torso / thorax |
| C3 | abdomen / digestive |
| C4 | upper limbs |
| C5 | lower limbs / tail |

### Archivist Extension (added in the vault, v0.0.1)

Built by the doctor after the golem fell, when the iguana addressed Azazel. The party had not planned to extend the lexicon. The doctor had already mapped the empty space.

| # | Root | Noun | Verb | Adjective |
|---|---|---|---|---|
| 24 | C4 · M | expression / voice | express | expressive |
| 25 | C4 · B | record / archive | write / record | written |
| 26 | C5 · S | gold / treasure | conceal / bury | concealed / buried |
| 27 | C5 · M | the other / that one | remain | remaining / still |
| 28 | C5 · B | ground / earth | send away / release | sent / gone |
| 29 | C2 · B | boundary | bind / contain | bounded / contained |
| 30 | S · C2 | absence / nothing | vanish / disappear | unseen / no longer seen |
| 31 | M · C2 | lie / concealment | conceal / lie | false / hidden (deliberate) |
| 32 | B · C2 | question / unknown | ask / seek | unknown / where? |
| 33 | S · C4 | the present | be present | now / current |
| 34 | M · C4 | that place / location | be there / locate | exactly there / right there |

---

## V. The Matthew 25:18 Reading

*Source: Matthew 25:18. "But he that had received one went and digged in the earth, and hid his lord's money."*

*The iguana does not mention a servant. This is a deliberate misreading. The demonstrative "that" is read as the article-pointer G alone, not as "he that." The one is a numeral. The gold is sent with the concealment already on it. The expression is what remains. The goat is sent. The lie remained. This is the reading the doctor gave after the party decided Azazel was not a villain. The reading is the operator's. The misreading is deliberate. The art is the reading.*

**Acoustic notation** (partial; forty-three sounds total):

```
G  ·  C1  ·  M  ·  G  G·C4·M  ·  G  ·  S·C4·G  M·G·C2  ·  C2·B·G  B  C2·B·G
G·C5·S  C5·S·G  ·  C5·G·B  ·  S·C2·G  ·  C5·M·G  M·G·C2  ·  G  G  C5·M·G  ·
G·B·C1  ·  S·C4·G  G·C4·M  ·  G·C4·M  C4·G·M  G·C5·S  G·C4·B  ·  M  ·  M  ·
G·C5·M  G  ·  G·C5·M  G  ·  S  ·  M·C4·G  ·  B·C2·G  M·G·C2  ·  G·B·C1
G·C4·B  G  ·  G·C4·M  C5·G·B  ·  G·C4·M  M·C4·G  ·  G·M·C2  C5·G·B  ·
G·M·C2  C5·M·G  ·  M·C4·G  ·  G·C4·M  ·  G
```

**Lisbeth's rendering** (as spoken in the vault, 2026-10-31):

> That. One. On the other hand. The expression. This. Now lies. Bounded and contained. Gold concealed. Sent. No longer seen. Still lies. This that was that. Then. Now expression. Expresses gold in speech. But. On the other hand. Just that. Just that. No! There. Exactly where? What was taken? That is written. The expression sent. The expression there. The lies were taken. The lies remained. Exactly there! The expression. That.

---

## VI. Usage Notes

**Message and minimum amplitude:** the Message cantrip transmits sound to a target without specifying a floor on volume. A breath hiss below the threshold of ambient hearing is still carried. The iguana's full dynamic range is available.

**Wild shape and mental capacity:** a druid in wild shape retains their full Intelligence, Wisdom, and Charisma scores. The iguana understands Common and every other language the druid knows. The constraint is outgoing: an iguana cannot produce human phonemes. Scratch is built entirely from sounds an iguana's anatomy can produce — forced glottal expiration (the glottal click), controlled air expulsion (hiss spectrum), and claw taps on hard surfaces. The Message spell carries the iguana's side of the exchange back to Lisbeth as acoustic data. She translates.

**Scratch is not a natural language.** It has no history, no speakers outside this party, and no literature except what the doctor builds into it on the index card. The doctor objects to this situation. The doctor is working on it.

---

## VII. Known Gaps (v0.0.1)

The doctor has identified the following as unaddressed in the current lexicon:
- Tense beyond the present/past distinction in adj-34 and B·C1 (time)
- Proper names and unique referents
- Conditionals ("if")
- The specific vocabulary of surgery below the torso without the anatomical coordinate system
- Any word for "I" or "you" (the language has no first-person pronoun; the doctor objects)

*v0.0.2 pending. The doctor is aware.*

# ElevenLabs Voice Design Prompts

Feed each prompt into ElevenLabs → Voices → Voice Design (v2). Generate 3–5 samples per prompt, pick the best, then update `generate_audio.py` VOICE_MAP with the resulting voice ID.

---

## Winslade
*Hegemony officer. Undying Mercenaries. Formal, bureaucratic, precise. Replaces Carter.*

```
American male, early thirties, hint of a Queen's English accent. Baritone with institutional weight — the voice of a man who has filed many reports and knows that the report is the record, and that the record is kept by the man who files the report. Measured pace, clean diction. No warmth, some concern, some suspicion. Nasally. The authority is personal and vain, but he tries to do his best. He raises his voice when he believes plans are falling apart.
```

**Use for:** Winslade dialogue on construction site, site inspection, administrative decisions.  
**Replaces:** Carter (`MwdOFxwRC5Rru2LQ0DnY`) in VOICE_MAP.  
**Add as:** `"Winslade"` in VOICE_MAP.

---

## Happy Gilmore
*Construction site. Deadpan. Found his center.*

```
American male, mid-thirties. Working-class register. Slightly flat affect — not sad, not bored, just unbothered. The voice of a man who has done this before and will do it again and that is fine. Moderate pace. Nasal undertone. Never performs surprise. Occasional laconic humor, delivered at the same volume as everything else.
```

**Use for:** Happy Gilmore construction site scenes. Nail gun sequences.  
**Replaces:** current Chandler placeholder (`IKne3meq5aSn9XLyUdCD`).  
**Update:** `"Happy"` in VOICE_MAP.

---

## Merlin
*Noir Sherlock Holmes as Benedict Cumberbatch. Slight Babylonian accent.*

```
British RP male, mid-forties. The base is Sherlock Holmes — crisp consonants, fast interior rhythm, slightly contemptuous precision. Layered with noir: the register is lower, gravel in the chest, world-weary without being defeated. The Babylonian accent is a ghost, not a feature: slight elongation on certain vowels, a subtle Levantine weight on gutturals, as if the voice has memory of a language older than London. He deduces. He is tired of deducing.
```

**Use for:** Merlin scenes. Deduction sequences. Any moment where the knowledge is certain and the patience is not.  
**Add as:** `"Merlin"` in VOICE_MAP.

---

## Lisbeth
*Lisbeth Salander. Better than Matilda.*

```
Swedish female, late twenties. Low pitch for a woman — not artificially low, simply not performing softness. Flat affect that is not robotic: she has feelings and does not display them. Swedish English: precise vowels, slightly clipped rhythm, the accent present but not theatrical. Fast when she speaks. She doesn't speak often. When she does, the sentence is already complete before she starts it.
```

**Use for:** Lisbeth Salander — all pages. Danish/Swedish sections.  
**Replaces:** Matilda placeholder (`XrExE9yKIg1WjnnlVkGX`).  
**Update:** `"Lisbeth"` and `"LisbethEn"` in VOICE_MAP.

---

## Witch of the Rivers
*Cleopatra in essence. Not in lineage.*

```
Female, timeless register — the age is not audible. Deep contralto. Mediterranean and North African warmth, the kind that carries absolute authority without raising itself. She does not perform power; she is the reference point for it. Unhurried, each word allowed its full weight. A slight ancient quality — not archaic, not theatrical, but as if the language learned to flow through her rather than the other way around. The river knows where it goes.
```

**Use for:** Witch of the Rivers — all pages including −08 and the Rivers section.  
**Replaces:** Lily placeholder (`pFZP5JQG7iQjIQuC4Bku`).  
**Update:** `"Witch"` in VOICE_MAP.

---

---

## Auden
*W.H. Auden. Narrator of −30. Present at the dock. Has a notebook.*

```
British-American male, late fifties. Yorkshire-born but thirty years in New York have moved the vowels — the accent is transatlantic: the consonants stay British, clipped and deliberate; the vowels have drifted mid-Atlantic, neither RP nor American. Dry and slightly nasal, moderate resonance, never loud. The pace is measured with genuine pauses — not theatrical pauses, pauses where something is being noted. The irony is in the baseline, not the performance: he says the driest things in the same tone as everything else, and that is what makes them dry. He is not reading aloud; he is dictating to a notebook. The voice of a man who has been paying close attention for a very long time and has stopped expecting to be surprised and is still sometimes surprised.
```

**Use for:** Auden narration in −30. All italicised narrator lines.
**Add as:** `"Auden"` in VOICE_MAP.

---

## Holden
*Holden Caulfield. Sixteen. New York. Phony-detector.*

```
American male, New York. Mid-range, slightly nasal. The register sits unresolved — not committing to either end of its range. Inflection rises at the end of uncertain statements and drops completely flat at the end of certain ones; these two patterns alternate and neither is theatrical. Fast tempo when agitated, unexpectedly slow when genuine. Default emotional coloring is skepticism: a slight withholding quality, as if the speaker is always slightly ahead of his own sentence and leaving room to revise it. Educated register, but the education is deliberately underperformed — the casualness cost some effort to achieve. Upper Manhattan, no street affect.
```

**Use for:** Holden dialogue in −30.
**Add as:** `"Holden"` in VOICE_MAP.

---

## Gatsby
*Jay Gatsby. Thirty-two. Self-created. Looking at the light.*

```
American male, early thirties, with a practiced mid-Atlantic quality — he grew up somewhere flat and spent years constructing a different voice and mostly succeeded. Smooth, warm, the warmth is genuine but learned, which is not a contradiction. Moderate pace with deliberate pauses — he learned to pause. The control is the tell: nothing is accidental. A slight softness on certain words, as if the performance slips just enough to show the thing beneath it. In quiet moments the voice drops further — less construction, more the person who stands at the dock and looks at a light and doesn't stop. Never performs sadness. The sadness is in the precision.
```

**Use for:** Gatsby dialogue in −30.
**Add as:** `"Gatsby"` in VOICE_MAP.

---

## Atticus
*Atticus Finch. Fifty. Maycomb, Alabama. The suit in court was explicit.*

```
American male, fifty, Alabama. Deep baritone — not performed deep, simply where the voice lives. The Southern cadence is unhurried: not because he is slow, but because he is certain enough to take his time. The accent is present in the vowels and the rhythm — moderated by education, never erased. The voice of a man who has spoken in courtrooms and understands that the weight of a word is partly in how long you take to say it. Not theatrical — the opposite of theatrical; theater would be the wrong instrument for what he is doing. Genuinely warm, not performed warm. When he says something important he says it at the same volume as everything else. He does not raise for emphasis. He lowers.
```

**Use for:** Atticus dialogue in −30.
**Add as:** `"Atticus"` in VOICE_MAP.

---

---

## Shakespeare
*Narrator of −35. Sets the stage. Annotates the labyrinth. Never moves.*

```
British male, mid-fifties, Elizabethan stage tradition carried in weight not diction.
The accent is late-Renaissance RP — precise consonants, measured pace, nothing wasted.
He is the playwright-as-narrator: he has seen the scene before it happened and is
recording it accurately. Each sentence is architecture — load-bearing pauses, words
that earn their position. Dry wit in the baseline, never performed. The irony is
structural, not theatrical. He does not raise his voice. He does not need to.
When he says something important, he says it at the same volume as everything else.
He is not reading aloud; he is annotating a notebook.
```

**Use for:** Shakespeare narration in −35. All stage-setting passages.
**Settings:** stability 0.62, similarity_boost 0.80, style 0.15, use_speaker_boost true.
**Add as:** `"Shakespeare"` in VOICE_MAP via `.env` `VOICE_SHAKESPEARE=<id>`.

---

## Chaucer
*Orator of −35. The herald in tournament regalia. Delivers the performance.*

```
British male, mid-thirties. Exuberant in the original sense — joyful, showy,
delighted by his own words, theatrical without being dishonest. This is the
Geoffrey Chaucer who gambled away his clothes and found it clarifying, who
introduces knights in full tournament regalia with total commitment, who makes
Sir Ulrich von Lichtenstein real by saying so out loud with full conviction.

The register is vernacular RP — neither archaic nor modern — fast-moving,
highly variable: he can slow to a whisper mid-sentence and then suddenly ring
out at full volume and it sounds correct both times. The rhythm changes with
the content. He rises on revelation. He drops to conspiratorial near-silence
for an aside. He laughs mid-sentence sometimes, not out of nerves but delight.

There is no ironic distance between him and what he says. He means every word.
The flamboyance is not performance anxiety — it is the confidence of a man who
knows that the announcement makes the thing real, and he has practiced this,
and he is good at it, and he is glad to be doing it right now in front of you.
```

**Use for:** Chaucer oration in −35. Verbatim VOLARE passages, the verse, Matthew 25:18.
**Settings:** stability 0.32, similarity_boost 0.70, style 0.58, use_speaker_boost true.
**Update voice in ElevenLabs → Voice Design → regenerate → paste new ID as `VOICE_CHAUCER` in `.env`.**

---

## Notes on generation

- Generate at **stability 0.45, similarity 0.75, style 0.30** for character voices (more expressive).
- Generate at **stability 0.65, similarity 0.80, style 0.15** for Lisbeth (controlled, flat).
- Merlin: try **stability 0.40, style 0.40** — the contempt and the noir need to bleed through.
- Witch: try **stability 0.55, style 0.50** — unhurried but not monotone.
- **Auden: stability 0.60, similarity 0.80, style 0.20** — precise and controlled but not flat; the irony needs room.
- **Holden: stability 0.35, similarity 0.70, style 0.45** — most expressive of the four; the register needs to be able to go flat AND go up AND go fast.
- **Gatsby: stability 0.50, similarity 0.75, style 0.30** — controlled warmth; the slippage moments need to read as the performance briefly dropping, not as inconsistency.
- **Atticus: stability 0.68, similarity 0.82, style 0.12** — the most controlled voice; very low style variance; the weight comes from certainty not expression.
- After generating, run a short test segment from the relevant page before committing the voice ID.

---

## VOICE_MAP additions (pending voice creation)

```python
# Add these to generate_audio.py VOICE_MAP once voice IDs are in hand:
"Winslade":  "PENDING",   # see VOICE_DESIGN_PROMPTS.md
"Merlin":    "PENDING",   # noir Sherlock / Babylonian
# Update these:
"Happy":     "PENDING",   # replace Chandler placeholder
"Lisbeth":   "PENDING",   # replace Matilda
"LisbethEn": "PENDING",   # same as Lisbeth once created
"Witch":     "PENDING",   # replace Lily
"Auden":     "PENDING",   # narrator of −30; transatlantic, dry, notebook
"Holden":    "PENDING",   # sixteen, New York, phony-detector
"Gatsby":    "PENDING",   # self-created, practiced warmth, looks at the light
"Atticus":   "PENDING",   # Alabama baritone, courtroom cadence, lowers for emphasis
```

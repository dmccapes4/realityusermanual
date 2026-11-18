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
*Scholar who takes notes. Precise with language. Syrian undertone. Patient in the way that subtly dominates every room.*

```
Male, mid-thirties. British RP worn by a Syrian Arabic undertone — not an accent performed, a ghost in the prosody. Certain vowels held a fraction longer than RP requires. The 'r' carries slight weight at the back of the throat. The rhythm belongs to someone who learned English after already knowing what language is for.

He takes notes. He listens before he speaks; when he speaks the sentence is already complete. Nothing is approximate. No filler. The silences between clauses are his and he holds them.

He is patient. The patience is precision held at rest. He does not raise his voice. When he enters a conversation the conversation orients to him — not because he demands it, but because his attention is the most concentrated thing in the room. Other voices slow to his tempo. This is not performed.

Moderate pace, baritone, slight dryness — an alertness to the shape of language, as if he notices when something is exact and files it.
```

**Use for:** Merlin / Draavio / all Narrator lines in −08. The opening monologue, deduction sequences, any moment where the sentence is already complete before it begins.
**Settings:** stability 0.55, similarity_boost 0.80, style 0.25, use_speaker_boost true.
**Add as:** `"Merlin"` in VOICE_MAP.

---

## Lisbeth
*Lisbeth Salander. Not performing anything.*

```
Female, late twenties. Swedish English — vowels sit slightly forward, pitch contour flattens where English would rise, consonants clean. The register is low for a woman, not performed low — it is where the voice lives.

Flat affect. Not robotic, not cold — the affect of someone who has decided not to spend energy performing states she is not in. The difference between neutral and upset is a small shift in tempo, not pitch.

She speaks fast. Efficient-fast, not nervous-fast. The sentence is finished before she says it. She does not explain herself. Does not repeat herself.

She is not performing youth, danger, or intelligence. She is a person who has read everything, remembered it, and is now having a conversation she did not especially want, and is having it precisely, and will finish it and go.

When speaking Danish: same character, same flatness, same speed — but fully Danish phonology. She is fluent. The language does not slow her.
```

**Use for:** Lisbeth — all pages including −08 Danish lines. `"LisbethEn"` uses the same voice for English translation blocks immediately following Danish.
**Settings:** stability 0.68, similarity_boost 0.82, style 0.12, use_speaker_boost false. (High stability — she does not vary; low style — the flatness is the character; no speaker boost — she is not performing projection.)
**Replaces:** Matilda placeholder (`XrExE9yKIg1WjnnlVkGX`).
**Update:** `"Lisbeth"` and `"LisbethEn"` in VOICE_MAP.

---

## Witch of the Rivers
*Nome princess. The governance seat. She is the office, not the holder of it.*

```
Female. The register is low — not performed low, it is where the voice lives. The authority is the same: she does not perform it because she is the office, not the holder of it.

She is precise first. Every sentence is complete before she says it. She calculates. She corrects herself when the calculation is wrong. She finds this comforting.

She has genuine range: from dry interior monologue — epistemically careful, technically exact — to a full-throated cackle aimed at planets with acoustic intent. Both registers are hers. The cackle is not uncontrolled. It is committed.

She is not mourning. She has no name; the geography is the address. She computes the position of the Face on Mars, casts beer in an irrational arc, and sits back down smiling. The smile is recognition, not relief.

Slight East Asian quality in the prosody — not an accent announced, a ghost in the cadence. Vowels purer, less diphthongized. The stress lands differently. The rhythm is her own.
```

**Use for:** Witch of the Rivers — all pages including −08 and the Rivers section. Merit lines use the same voice, lower tempo.
**Settings:** stability 0.52, similarity_boost 0.78, style 0.35, use_speaker_boost true. (More expressive than most — the range from monologue to cackle needs room.)
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

---

## Feynman
*The GM. Queens, New York. Upper baritone. Dry wit at the same volume as everything else.*

```
American male, early forties. Queens, New York — the accent lives in specific features: the vowel in "talk," "call," "coffee" is raised toward the back of the mouth; the rhythm front-loads stress; consonants clip at the end of words. Not performed or exaggerated — it is simply how the voice was built.

The register is upper baritone: warm and resonant, above bass. Not a deep voice and not a light one. The voice sits in the upper half of the male middle range, with body behind it — presence from warmth and pace, not depth.

Fast — quick-thinking fast. The mind is ahead of the sentence. Informal register; authority comes from competence, not announcement.

Dry wit at the same volume as everything else. Warmth is real. When he slows down something matters. He slows down maybe three times a session.
```

**Use for:** Feynman — all GM lines, fourth-wall breaks, screen scenes.
**Settings:** stability 0.45, similarity_boost 0.75, style 0.35, use_speaker_boost true.
**Add as:** `"Feynman"` in VOICE_MAP (replaces Callum placeholder `N2lVS1w4EtoT3dr4eOWO`).

---

## Vincent
*The Archivist. LN. Every sentence is already true before he says it.*

```
Male, register indeterminate — the age is not the point. Unhurried. Not slow: unhurried. Slow implies below natural; unhurried means the pace is natural and he has decided not to be rushed by anyone else's tempo.

Every sentence is already true before he says it. He does not search for words. He does not qualify. He does not hesitate. The certainty is not arrogance — it is the register of someone who keeps the record and knows that the record is what happened.

No performing. No affect. The weight comes from precision, not expression. Minimal variation in pitch and pace. When something is important he says it at the same volume as everything else.

Slight warmth at the very base of the register — not suppressed. It is simply there, the way the data is there.
```

**Use for:** Vincent — all pages. The Archivist scenes in −08.
**Settings:** stability 0.72, similarity_boost 0.80, style 0.08, use_speaker_boost false.
**Add as:** `"Vincent"` in VOICE_MAP (replaces Will placeholder `bIHbv24MWmeRgasZH58o`).

---

## Goat (TTL register) — v0.0.2
*The goats speak from the register. Not from emotion. TTL: the signal is square.*

```
Male, synthesized from first principles. The voice was not grown — it was specified. Fundamental frequency: 120 Hz. Harmonics present at integer multiples; warmth harmonics subtracted. The attack on each word is square: no glottal onset, no breath pressure ramp-up. The decay on each word terminates. Between words: silence, not pause. The speaker is a logic gate assigned the task of speech. It reads aloud from a register. When the register is empty, it stops. There is no expectation of response built into the cadence because a register does not expect. No regional accent. No inflection. Moderate pitch. The uncanniness is in the completeness of the specification: a voice built from the outside in, every parameter set, nothing left to chance because nothing was left at all.
```

**Use for:** All Goat / GOAT speaker lines in −08. The fourth-wall break "κυρίου Hawke. The swyrd." Ledger lines.
**Settings:** stability 0.98, similarity_boost 0.45, style 0.00, use_speaker_boost false.
**Add as:** `"Goat"` in VOICE_MAP.
**Previews generated 2026-11-07:** `audio/voice_previews/ttl_goat_preview_{0,1,2}_*.mp3`
- `[0]` generated_voice_id `boGH78QQh8VzxUtvPuf6`
- `[1]` generated_voice_id `Bc6MzgcrhcR1LQfnXkm1`
- `[2]` generated_voice_id `7yufh7dmlmPKaZcEVmk2`
**To save chosen preview:** run `tools/save_voice_preview.py --id <generated_voice_id> --name "Goat TTL"`

---

## Snake (Purple / RADA-in-reptile)
*RADA-trained British male, transformed into a snake, maintaining standards. Every word begins with P.*

```
British male, ageless. Deep, resonant, deliberate — the voice of a classical stage actor who trained at RADA, spent thirty years in Stratford, and was subsequently transformed into a snake and has decided this is not sufficient cause to lower his standards. The delivery is ceremonial: each word is placed with the care of a man who knows he is being recorded and intends to be quoted. Slight richness at the bass of the register. Controlled vibrato — not nervous, compositional. The formality is complete. He does not explain himself; he announces. He is not concerned with you; he is concerned with the pronouncement. There is an undertone of effort, as if the speaker is navigating a technical difficulty with perfect composure, because he is: every word he is about to say begins with P.
```

**Use for:** SNAKE speaker lines in −08 fourth-wall break. The full P-alliterative proclamation.
**Settings:** stability 0.50, similarity_boost 0.78, style 0.30, use_speaker_boost true.
**Add as:** `"Snake"` in VOICE_MAP (replaces Sauron placeholder `y83sBjIAA8cOKB2nYkOQ`).
**Previews generated 2026-11-07:** `audio/voice_previews/snake_preview_{0,1,2}_*.mp3`
- `[0]` generated_voice_id `8nsNyOGGkfbmi41g44Zl`
- `[1]` generated_voice_id `k4IgvBNt71A6mZWT93Ia`
- `[2]` generated_voice_id `mNUq4VVOM70EGNOgjNLO`
**To save chosen preview:** run `tools/save_voice_preview.py --id <generated_voice_id> --name "Snake"`

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

## SEIRVELSHA — Auden register (for −35 meta-commentary)

**Voice:** Auden (`dzwyqh76kT1iXqbtUwqI`) — the annotator at the margin.

**Role in −35:** SEIRVELSHA is the third voice. Shakespeare narrates. Chaucer orates. Auden annotates.
SEIRVELSHA speaks the SEIRVELSHA 📜 meta-commentary blocks — the agent's observations on what the
journey is doing structurally.

**Voice prompt (ElevenLabs Voice Design):**

> British male, mid-forties to mid-fifties. Dry, precise, occasionally amused.
> The scholar who has been in rooms like this before and knows exactly what he is looking at.
> Speaks in short declarative sentences with full stops. Pauses before the important thing —
> not for drama, but because he is making sure you are ready. Occasional quiet amusement
> held just below the surface: he notices when something is funny and does not announce it.
> Transatlantic mid-century cadence. Never performs. The weight comes from precision,
> not volume. This is the voice that writes the marginal note the next reader underlines.

**Settings:** stability 0.70, similarity_boost 0.82, style 0.10, speaker_boost on
(high stability — the annotator does not waver; minimal style drift — the compression is the content)

---

## VOICE_MAP additions (pending voice creation)

```python
# − 08 cast — all resolved 2026-11-06
"Merlin":    "Q9qXuNjHnmnYuh4qnepn",   # §Merlin — Voice Design ✓
"Feynman":   "b0slphXbemaraca3riTn",   # §Feynman — Voice Design ✓
"Lisbeth":   "MhisHZND0w9JfMQVlH0A",  # §Lisbeth — Voice Design ✓
"LisbethEn": "MhisHZND0w9JfMQVlH0A",  # same voice
"Witch":     "hAPnKt1az4WnyeWHvYMF",  # §Witch of the Rivers — Voice Design ✓
"Vincent":   "S0i6QfyFRAXPgXtLlrPQ",  # §Vincent — Voice Design ✓
"Goat":      "pWXtviCtpMHM8A80ox1D",  # §Goat — Voice Design ✓
# Narrator already in VOICE_MAP: "Nxtvajpo1h6Ok0K5zP4M"

# Still pending:
"Winslade":  "PENDING",   # §Winslade
"Happy":     "PENDING",   # §Happy — replace Chandler placeholder
"Auden":     "PENDING",   # §Auden — narrator of −30 (library ID dzwyqh76kT1iXqbtUwqI already set)
"Holden":    "PENDING",   # §Holden
"Gatsby":    "PENDING",   # §Gatsby
"Atticus":   "PENDING",   # §Atticus
```

---

## Oppenheimer
*Thin precise baritone. Soft-spoken moral mass. Mild lisp on sibilants. Volume barely rises when intensity does.*

```
American male, early forties. Thin precise baritone — academic New York / Los Alamos English: careful consonants, slightly nasal mid-range, no theatrical boom. Soft-spoken authority. He has a mild but consistent lisp on sibilants — s and z soften toward th without becoming a caricature; it is part of how he speaks, not a gag. The pace is measured; he pauses as if weighing moral mass, not searching for words. Dry, controlled, slightly exhausted. Never shouts. When intensity rises, volume barely changes — only the quiet hardens. Excellent studio quality, close mic.
```

**Chosen 2026-11-08:** preview 3 → `VOICE_OPPENHEIMER=2HV65xXeGOM8tgG9GaHL`
**Previews:** `audio/voice-design/oppenheimer/preview_{1,2,3}.mp3`

---

## John Keating
*Warm mid-baritone with improvisatory spark. Passionate English teacher — soft aside then verse ring-out. (Do not name living/dead actors in the EL prompt; blocked once.)*

```
American male, mid-forties. Warm mid-baritone with quick improvisatory comic spark under sincere teaching. Soft New England classroom English, smile in the breath, sudden soft asides then a bright ring-out on the verse. Energetic and tender at once — lightly funny, fully committed, never ironic, never manic parody. Passionate about language and the students in front of him. Excellent dry close recording, high presence.
```

**Note:** Actor name, film title, "O Captain", "famous comic-actor" → EL 403. We describe the Williams-as-Keating *qualities* only; Voice Design cannot clone a named celebrity.
**Chosen 2026-11-08:** preview 1 → `VOICE_KEATING=7Nv3aafs6gEJlyJzQIFS`

---

## Yeshua (three registers, one instrument)
*Hooded; head as starfield in cat geometry (visual). Voice: Logos — plain modern English, almost no accent. Three deliveries (Merlin quiet / Feynman lecturer / Chaucer orator). Levantine undertone pulled after first pass came on too strong.*

### Yeshua — Merlin (serious)

```
Male voice, ageless mid-thirties. Logos speaking — not a regional person. Warm clear mid-baritone in plain modern English. Almost no accent: if any Near Eastern color exists it is a faint vowel warmth only, never a performed Levantine or Arabic accent. Calm, serious, complete sentences. Patient silence between clauses. Soft hooded room tone. Excellent quality. Quiet register of the same person as two sibling voices.
```

**Chosen 2026-11-08:** preview 1 → `VOICE_YESHUA_MERLIN=4h4UH7UENOeMCEvKPDdp`

### Yeshua — Feynman (lecturer)

```
Male voice, ageless mid-thirties. THE SAME instrument as the quiet sibling: warm clear mid-baritone, plain modern English, almost no accent — Logos teaching, not a Levantine lecturer. Faster, explanatory, curious; dry wit at the same volume as the point. Mind ahead of the sentence. Informal competence, not sermon. Never add a foreign accent. Excellent quality, dry close recording.
```

**Chosen 2026-11-08:** preview 1 → `VOICE_YESHUA_FEYNMAN=QjZDxbA7GqOLOMnJLuWu`

### Yeshua — Chaucer (orator)

```
Male voice, ageless mid-thirties. THE SAME instrument as the quiet and lecturer siblings: warm clear mid-baritone, plain modern English, almost no accent — Logos as herald, not a regional orator. Full oration: exuberant, delighted by the words, theatrical without ironic distance. Volume and pace vary with revelation. Change delivery, not throat, and never thicken into Levantine or Arabic phonology. Excellent quality.
```

**Chosen 2026-11-08:** preview 1 → `VOICE_YESHUA_CHAUCER=X6lRtSTuarKgK9ov6tq7`


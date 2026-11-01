# GAME PLAN — GrammaticalGeometrySpaceDriver

**Date.** 2026-11-01
**Subject.** A tool that walks a verse and keeps the measure.
**Brief.** Operator, 2026-11-01. Game plan first. No build in this file.
**Name.** GrammaticalGeometrySpaceDriver

---

## 1. Why a tool

The etymology and the philology have been done by hand, because agents have not been trustworthy on Greek Koine or on ancient Semitic languages against drift over time. Leaving the agents out of that work did not remove the cost. It moved the cost into the accounting. The record is worth having. Agents are good at the record a lot of the time. They are not the authority on the drift.

The tool is the method, written down so a run keeps what it measured. A report files the run. The report does not call the operator an immoral liar. The report does not pretend authority he did not give.

If a thing has happened at least once, the question of how many times is a logical consequence. The measures that would answer it were not kept. This plan does not count them. The driver is so the next walk keeps its own measure.

---

## 2. What it is

A deterministic walker over one verse.

The script decides the order. The order is the letters, then the word, then the next word, until the verse ends. A model may fill a schema. It may not choose where to start, which word to skip, or which gloss wins. Temperature is 0 when the interface allows it. One model per run. The model id is a string he sets. The run refuses the model step until that string is set.

He said GPT-4.1 is pretty good, and that he hears Sonnet 3.5 is the best. The driver does not pick between them. He will provide an Anthropic key. The plan does not look for a key. The key and the model id are configuration he supplies. They are not read back into a report.

There is no second model that grades the first. A line that fails the schema is stored as failed, with the raw output beside it. It is not sent back with a hint.

---

## 3. Sources

**greekbible.com** is the Bible source. It provides the verse text and available translations. He uses the translations conveniently. The agent retrieves them and stores all of them as candidates in the `translations` array. The agent does not choose which translation wins. The site uses JavaScript for rendering; the scraper has a `--greek` flag for manual text supply when retrieval returns empty.

**logeion.uchicago.edu** is a collection of dictionaries. Each dictionary is a separate witness with its own `source_id`. The site is esteemed, and wariness is warranted. As of 2026-11-01, no public JSON API was confirmed. Retrieval uses the web interface and parses each dictionary's section separately. If an API is found, the retrieval function in `sources.py` is updated there and nowhere else.

Known dictionaries within Logeion and their source_ids:

| Display name | source_id |
|---|---|
| Liddell–Scott–Jones (full) | logeion_lsj |
| Middle Liddell | logeion_middle |
| Lewis & Short | logeion_ls |
| Slater (Pindar) | logeion_slater |
| Cunliffe (Homer) | logeion_cunliffe |
| Dodson (NT) | logeion_dodson |
| Thayer (NT) | logeion_thayer |
| Abbott-Smith (NT) | logeion_abbott_smith |
| Muraoka (LXX) | logeion_muraoka |

A retrieval is stored with its URL and its timestamp. A gloss from any dictionary is a witness in the primitive. It is not the meaning of the word. If two dictionaries differ, both members stay.

Ancient Semitic drift is the other place agents have failed him. It is not in the first run. A later source is a plugin with the same rule: store the retrieval, do not let it spend the set. It is not added by the model in the middle of a verse.

---

## 4. The kernel

Each verse has a kernel. In this plan the kernel is the stored object, not a sentence about the verse.

- The reference, as he names it.
- The retrieved text, in order.
- The JSONL of primitives.
- The eliminations, each tied to a rule already stored.
- The set that remains.

The kernel does not contain a line that says what the verse means. That line is an interpretation. It enters only as a member of `possible_interpretations`, and only as possible.

---

## 5. The file

One JSONL per verse. One JSON object per word. An article is a word. The line order is the verse order.

He named the fields. Two of the names need a yes before a build, because the singular and the plural do not match. Until that yes, this is the proposed line.

```json
{
  "meta_data": {
    "timestamp": "",
    "model_id": "",
    "sources": []
  },
  "verse": "",
  "word": {
    "surface": "",
    "letters": []
  },
  "description": "",
  "grammatical_rules": [],
  "lexical_rules": [],
  "semantic_rules": [],
  "translations": [],
  "possible_interpretations": [],
  "edges": []
}
```

`semantic_rules` is the proposed plural, parallel to the other two rule arrays. He wrote `semantic_rule`. The build keeps his key if he says the singular stays.

Anything else the walk needs is an added key, named in the report, not a silent field. A proposed key does not become part of the schema until he consents.

---

## 6. The walk

The ten steps, as the driver will run them.

0. Retrieve the verse and the lexical entries from the two sources. Store them in `meta_data` with the timestamp.
1. Open the kernel for that verse. Empty JSONL. No gloss in the kernel.
2. For each word, open one primitive.
3. Letter by letter, record what the letters are. A letter is a glyph in order. It is not given a meaning by the model.
4. Store the grammatical properties, the lexical properties, and the semantic properties that the sources state for this word. Each rule carries the source and the quotation. A rule the model infers is marked proposed. A proposed rule cannot eliminate anything.
5. Record patterns when they are visible. The kinds he named: symmetric looking; dramatic language in a popular reading; a deliberate misspelling; a change an institution decided on. A pattern is an edge or a note on the primitive. It joins words. It does not delete a translation.
6. List the translations that still stand, given this word and the words already built. A translation stands when no consented rule and no source quotation contradicts it.
7. If this word contradicts a translation on an earlier word, append an elimination on that earlier word. The earlier translation remains in the primitive, marked eliminated, with the rule id and the timestamp. It is not deleted. Then finish this word's primitive.
8. Continue until the last word.
9. Ponder. Write what remains open. Do not write "it means this" while more than one member remains. If one member remains because every other member was eliminated by a stored rule, say that, and cite the rules. That is the only case in which the file may say the verse could only have meant one thing.
10. Write the report beside the JSONL. File both. The report lists the kernel, the retrievals, the eliminations, and the set that remains. It does not call him an immoral liar. It does not apply the label `his` unless he has explicitly requested it for that claim. It does not apply `measured` without naming the measure: which source, which quotation, which letters. A gap is written as a gap.

---

## 7. The word that carries three

He preserved, in one word, the three relations *but*, *on the other hand*, and *however*. Agents condemned the preservation.

The acceptance case for the driver is that word, in a verse he names. All three relations are stored in `translations`. A run that emits one of them and drops the other two fails. None of the three is eliminated unless a consented rule, or a quotation from one of the two sources, contradicts it. The popular reading is a pattern. It is not an elimination.

The plan does not name the Greek word for him. He names the verse and the word when he wants the first run.

---

## 8. Authority

A source quotation can contradict a translation. The model cannot.

Consent is a field on a proposed rule: unset until he sets it. The walker does not set it. A report that treats an unset proposal as a decision has pretended authority.

`possible_interpretations` are members shown so the set can be seen. They are not a creed about what the author meant. The author is said to have meant one member only when it is the only member left. He claims a reading of his own by saying so. The driver does not say it for him.

Working files of earlier derivations are not inputs. The driver does not open them to score the verse.

---

## 8b. Source agreement tracking (method)

He asked how to track which sources agree more often, and with whom, across runs. He named `sacred_concepts_atlas` and `nakatomi` as existing methods to review.

`nakatomi` is a financial portfolio engine (weekly weight shifts from price, inverse-vol, and news tilt). It is not applicable.

`sacred_concepts_atlas` uses a `sources` registry keyed by `source_id = text_language_version`, a `runs` table (model, params, timestamps, modelfile hash), and agreement measured through concept co-occurrence edges (co-occurrence + co-variance edges in Phase 4 of the atlas). The atlas then tracks which sections from different sources share concept signatures — those are agreements at the section level.

The GGSD adaptation:

Each dictionary in Logeion is a `source_id`. The driver already stores one entry per dictionary. For each word primitive, `compute_agreements()` in `schema.py` scans all rule fields and the `translations` array, and groups by `(field, value)`. If two or more `source_id`s independently state the same value for the same field on the same word, that is an agreement. The result is stored in `source_agreements` on the primitive.

Agreement rate per dictionary pair can be computed after a run by reading the JSONL and counting agreements where both source_ids appear together. A dictionary that agrees more often with another is one that independently states the same grammatical, lexical, or semantic properties for the same words. Divergence (one source_id only) is also stored — it is not silent.

The `report.md` displays agreements by word. A post-run analysis script (not yet built) will compute pairwise agreement rates across a corpus of runs.

The sacred_concepts_atlas principle that applies here: **the run is the unit**. Each walk of a verse is one run, with model_id and timestamps. The agreement data is per-run and can be diffed against a different model's run of the same verse.

---

## 9. Build status (2026-11-01)

**Built.** Files at `tools/ggsd/`:

| File | Role |
|---|---|
| `ggsd.py` | Main walker and CLI |
| `schema.py` | Primitive schema, validation, agreement computation |
| `sources.py` | greekbible.com and Logeion retrievals |
| `model.py` | Anthropic and OpenAI call layer |
| `report.py` | Report writer |
| `requirements.txt` | anthropic, openai, requests, python-dotenv, jsonlines, beautifulsoup4, lxml |
| `.venv/` | Project venv (gitignored) |

Dry run on Matthew 25:18 confirmed:
- `ANTHROPIC_API_KEY` reads from `REALITY_USER_MANUAL/.env` (106 chars, presence confirmed)
- greekbible.com scraper returns empty (site uses JavaScript — expected)
- `--greek` flag accepts manual text supply
- Run directory creates under `tools/ggsd/runs/`

**Next step:** supply the Greek text with `--greek` on the first real run.

```
.venv/bin/python ggsd.py \
  --verse "Matthew 25:18" \
  --model claude-3-5-sonnet-20241022 \
  --greek "ὁ δὲ τὸ ἓν λαβὼν ἀπελθὼν ὤρυξεν γῆν καὶ ἔκρυψεν τὸ ἀργύριον τοῦ κυρίου αὐτοῦ"
```

---

## 10. What the first build is, after a yes (original plan — now done)

The yes is the schema keys, the model id, and the verse. The key arrives from him. Then:

1. A project virtual environment and a `requirements.txt` for the driver only.
2. The schema, validated on write.
3. Two readers, one per source, storing the raw retrieval.
4. The walker, letter then word.
5. One model call per word, schema in, schema out, no retry loop.
6. The report writer, under the prohibitions in step 10.

The first verse is whichever verse he names. This plan does not choose one.

---

## 10. Out of the first build

- A count of older reports.
- A second model as judge.
- A search for an API key.
- Semitic as a hidden second walker.
- A sentence in the report that spends the set.

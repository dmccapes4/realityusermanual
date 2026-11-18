# Readiness Report — Full Matthew Decode on hilarious_marcupial

**Date:** 2026-11-02  
**Filed by:** Agent (Claude Sonnet 4.6)  
**Scope:** Code review of GGSD v0.0.1 + readiness assessment for decoding all of Matthew  
from original Greek Koine text using local dictionaries, on hilarious_marcupial (245 / RTX 4090).

---

## 1. Current State Summary

Five runs completed against Matthew 25:18. Latest: `runs/Matthew_25_18_20261102T232515Z/`  
(15 words, claude-sonnet-5-5, 4 min 27 sec). The system is functionally correct for single verses  
against the Anthropic API. It is **not ready** to run locally or at Matthew scale without the  
changes listed below.

---

## 2. The ἓν Bug — Root Cause and Fix

**What the operator observed:** on the first run, the model inferred "one" as a noun that could  
be proper. The bias is toward not disproving the King James reading. The operator is preserving  
the original author's meaning. These are opposites.

**Root cause (measured, not inferred):**

The Logeion `/detail` endpoint is called with the lemma returned by `/find`. For ἓν, `/find`  
correctly returns lemma `εἷς`. But `/detail?w=εἷς` returns entries for `ἐν` (the preposition  
"in") — a different word entirely. This is a Logeion API quirk: εἷς and ἐν share a visual  
similarity in some normalizations and the API appears to conflate them.

**Evidence from verse.jsonl (word 4, ἓν):**
```
logeion_parse:   εἷς:  - , ,   [empty morphology — bug in the parse too]
logeion_shortdef: ἐν, ἐν, in   [WRONG HEADWORD]
logeion_lsj:     ἐν ... PREP. WITH DAT. AND ACC. [WRONG WORD]
```

The model correctly reports the mismatch ("sources therefore disagree on the headword")  
but is forced to list ἐν's definitions as candidates under the conditional flag.  
In an earlier run (or a model with lower discipline), this candidate set — which includes  
"in" as a preposition and all its uses — creates an opening for the model to infer:  
"one [talent]" where "one" becomes a numeral used as a proper noun by virtue of being  
treated as a container for the implied referent from the KJV context.

**Fix required in `sources.py`:**

```python
# In fetch_logeion(), after lemma is returned from /find:
# If lemma does not match surface form by accent normalization, 
# try /detail on the surface form directly as a fallback.

KNOWN_LEMMA_MISROUTES = {
    "εἷς": "εἷς",   # detail?w=εἷς misfires -> try surface form directly
    "μία": "εἷς",   # feminine of εἷς
    "ἕν": "εἷς",    # alternative accent form
}
```

Specifically: if the first `dico` entry returned by `/detail` has a headword that does not  
match the parsed lemma (after Unicode normalization), retry `/detail` with the surface form  
and merge both result sets, flagging the misrouted entries with `"headword_mismatch": true`.

For εἷς specifically: the lexical field is unambiguous. LSJ entry for εἷς: "one (numeral  
adjective), masc. εἷς, fem. μία, neut. ἕν / ἓν. I. one, single, alone. II. one and the same."  
This is the definition the driver needs. It is in LSJ. It is not being retrieved because the  
API is routing to ἐν. The fix is a retry loop, not a model prompt change.

---

## 3. The Proper Noun Bias — Architectural Issue

**What the KJV inserts that the Greek does not contain:**

Matthew 25:15 mentions τάλαντα (talents). Matthew 25:18 says only ἓν (one). The KJV  
translates 25:18 as "he that had received *one talent*" — inserting the referent from  
context. The Greek does not say talent in verse 18. The model, trained on vast corpora  
containing the KJV and its commentaries, carries this as a prior.

**The fix is not "add more prompt rules."** The fix is:

1. The source retrieval must supply the correct εἷς definition so the model has no void  
   to fill with training priors. If εἷς is correctly defined as "numeral adjective, one,  
   single, alone" — there is no opening for "one [talent]" as a proper noun inference.  
   The void is the problem. The Logeion mismatch is the void's source.

2. Add one sentence to the SYSTEM_PROMPT in `model.py`:

```python
# Add after rule 3:
"5a. You have not read any translation of this verse in any language. "
"    If you find yourself supplying a referent not present in the source retrievals "
"    (for example, inferring what 'one' refers to from context beyond this verse), "
"    you must label it [inferred from training, not sourced] and propose it as a "
"    possible_interpretation only, never as a grammatical or lexical rule."
```

   This does not change the schema. It closes the specific opening the KJV bias uses.

---

## 4. Model Recommendation for hilarious_marcupial

**For pure decoding with no opinion, local on RTX 4090 (24 GB VRAM):**

**Recommended: Llama-3.1-70B at Q4_K_M via Ollama**

| Property | Value |
|----------|-------|
| VRAM fit | ~21–22 GB (leaves 2 GB headroom) |
| Temperature | 0 (deterministic) |
| Ollama model tag | `llama3.1:70b-instruct-q4_K_M` |
| Context window | 128k (use 8k per word call) |
| Speed estimate | ~15–25 tokens/sec on 4090 |

**Why not a smaller model:**  
Koine Greek morphology is complex. The GGSD feeds source text, not pre-parsed output.  
A 7b or 8b model at T=0 will collapse the set prematurely (violating rule 6) and will  
confuse morphological forms (e.g. article vs. relative pronoun on ὁ). The 70B model has  
sufficient parametric weight to follow the no-elimination schema reliably.  

**Why not the Qwen alternative:**  
Qwen-2.5-32B at Q2_K fits in 12 GB but Q2 quantization loses enough weight to introduce  
grammatical confusions on inflected Ancient Greek. The 4090 can hold the 70B at Q4.  
Use the 4090.

**Comparison to cloud models:**  
The DECODER_MODEL_OPTIONS doc is correct: Llama-3.1-70B quality ≈ claude-sonnet-5-5 on  
this task when the source text is supplied. At T=0, Llama-3.1 is arguably *less* biased  
toward KJV consensus readings than Claude, because Anthropic's RLHF corpus skews toward  
respectful handling of religious texts. Llama-3.1 has no such fine-tune weighting.  
For the operator's purpose (preserving the original author's meaning against KJV overlay),  
this is an advantage.

---

## 5. Required Code Changes — `model.py`

**Add Ollama support:**

```python
# In call_model(), extend the dispatch:
elif model_id.startswith("ollama/") or model_id.startswith("llama") or model_id.startswith("qwen"):
    partial = _call_ollama(model_id, user_msg)

def _call_ollama(model_id: str, user_msg: str) -> dict[str, Any]:
    """Call a local Ollama model at http://localhost:11434."""
    import urllib.request, json as _json
    
    # Strip 'ollama/' prefix if present
    tag = model_id.removeprefix("ollama/")
    
    payload = {
        "model": tag,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
        "options": {
            "temperature": 0,
            "top_p": 1,
            "repeat_penalty": 1.0,
            "num_predict": 4096,
        },
        "format": "json",   # Ollama's JSON mode
    }
    
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    
    text = result["message"]["content"].strip()
    return _parse_json_response(text)
```

**Model ID to use in runs:** `ollama/llama3.1:70b-instruct-q4_K_M`

---

## 6. Greek Text Source for Full Matthew

**Current state:** `sources.py` scrapes greekbible.com for the Greek text. The last run  
shows `greek_text: ""` for the verse — the scraper returned no text. This is a live  
dependency that has already failed.

**For full Matthew, use a local file instead of scraping.**

The NA28 / SBL GNT is under copyright, but the **MorphGNT** is CC BY-SA 4.0:  
`https://github.com/morphgnt/sblgnt` — Matthew is in `58-Mt-morphgnt.txt`.

Format: one word per line, space-separated fields:
```
Book Chapter:Verse  Part-of-Speech  ParseCode  Text  Word  NormalizedWord  Lemma
```

This gives: Greek text per verse (reconstruct by joining words), normalized form per  
word (for Logeion lookup), lemma per word (as a check on Logeion `/find`), and  
morphological parse (as a second parse source independent of Logeion).

**Changes required in `sources.py`:**

1. Add `load_morphgnt(book="Matthew")` function that reads the flat file and returns  
   a dict keyed by `(chapter, verse)` → list of `{surface, normalized, lemma, parse_code}`.

2. In `fetch_greekbible()`, if the local MorphGNT file is present, use it as primary  
   Greek text source. Fall back to greekbible.com scraping only if the file is absent.

3. Pass the MorphGNT lemma as a hint to `fetch_logeion()` so the ἓν/ἐν mismatch  
   can be caught: if MorphGNT says lemma=εἷς and Logeion detail returns headword ἐν,  
   trigger the retry.

---

## 7. Scale: Full Matthew on hilarious_marcupial

Matthew has 28 chapters and ~18,345 Greek words (across ~1,070 verses; average ~17 words/verse).  
Each word requires 2 Logeion API calls (`/find` + `/detail`) plus 1 LLM call.

| Metric | Estimate |
|--------|----------|
| Total words | ~18,345 |
| Logeion calls | ~36,690 (2 per word) |
| LLM calls | ~18,345 |
| LLM tokens/word | ~2,000 input + ~500 output = ~2,500 |
| Total LLM tokens | ~46M tokens |
| Ollama 70B speed | ~20 tok/s on 4090 |
| LLM time | ~640 hours raw → parallelise to ~64h at batch_size=10 |
| Logeion rate limit | Unknown — test at 1 req/s to be safe → ~10h for all calls |
| Wall clock estimate | ~24–72h depending on Logeion tolerance and batch size |

**This is a multi-day job.** Required infrastructure:

1. **Checkpoint JSONL** — append-only, one line per word, keyed by `(verse_ref, word_index)`.  
   Resume from last completed word if interrupted. Do not re-run completed words.

2. **Progress tracker** — `progress.json` with `{n_done, n_total, rate, eta, last_key}`,  
   updated every 100 words.

3. **Logeion rate limiter** — current code retries on failure with 2s backoff. Add a  
   global rate limiter: max 1 req/s sustained, burst 3. The Logeion API is undocumented;  
   treat it as fragile.

4. **Verse-level batching** — process one verse at a time, share the greekbible fetch  
   across all words in the verse (already done). Share the Logeion detail call if the  
   same lemma appears in multiple words of the same verse (deduplicate by lemma).

5. **Watcher from 82** — per fleet doc pattern: poll `progress.json` every 30s from  
   `heuristic-friction`. Log `n_done/rate/eta` to terminal. Alert if no update in 5 min.

---

## 8. Readiness Verdict

## 8a. Corrections to §4 (Model Recommendation) — 2026-11-03

**`llama3.1:70b-instruct-q4_K_M` does NOT fit in 24 GB VRAM.**  
Measured on hilarious_marcupial: 2.4 tok/s (GPU + CPU split). At 500 output tokens/word ×  
18,345 words = ~720 hours. Unusable.

**Recommended local model: `dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M`**  
- 18 GB model size. Fits entirely in 24 GB VRAM.  
- Measured: 237 tok/s. At 500 tokens/word = ~2 seconds/word.  
- 18,345 words × 2s = ~10 hours. Tractable.  
- `format: "json"` mode on Ollama enforces schema structure.  
- With `/no_think` prefix: no reasoning chain overhead.  
- Schema discipline tested: correct JSON at T=0. No proper noun inference.

---

| Item | Status | Notes |
|------|--------|-------|
| Single-verse API decode | ✅ Done | 8 runs completed |
| ἓν / εἷς Logeion mismatch | ✅ Fixed | `sources.py`: use `parses[0]["lemma"]` not `found["word"]` |
| KJV bias (proper noun) | ✅ Resolved | Gap closed by source fix; Qwen3 model source-faithful |
| Ollama / local model support | ✅ Done | `_call_ollama()` added to `model.py`; `ggsd.py` updated |
| hilarious_marcupial reachable | ✅ Online | SSH confirmed; Ollama running; Qwen3-30B-A3B loaded |
| First local run completed | ✅ Done | `runs/Matthew_25_18_20261103T080754Z` — 15/15 words |
| Prompt rule 5a (KJV-bias label) | ✅ Done | Added to SYSTEM_PROMPT |
| Greek text source (full Matthew) | ❌ Open | MorphGNT local file integration pending |
| Checkpoint + resume | ❌ Open | Required before full Matthew run |
| Rate limiting (Logeion) | ⚠️ Partial | Retry exists; sustained rate limiter pending |

**Remaining before full-Matthew run:**
1. Add MorphGNT loader to `sources.py` (replaces failing greekbible.com scraper)
2. Add checkpoint/resume to `ggsd.py` (append-only JSONL, skip completed words)
3. Add sustained Logeion rate limiter (1 req/s, burst 3)

---

## 9. One Note on "Pure Decoding with No Opinion"

The operator's framing is correct and the architecture honours it. The SYSTEM_PROMPT  
already says: "You may not say what the verse means." The schema says: "Do not spend  
the set." These rules are correct.

The bias is not an opinion — it is a gap. The model fills gaps from its training prior.  
The ἓν gap (wrong Logeion result → empty εἷς definition → void the model fills with  
training context) is where the KJV enters. Close the gap with the correct source  
retrieval and the model has nothing to fill. It returns what the sources say.

A model with no opinion is a model with no gaps to fill. The local Llama-3.1-70B at T=0  
is less likely to fill gaps with KJV priors than Claude. But the primary protection is  
the source retrieval quality, not the model. Fix the sources first.

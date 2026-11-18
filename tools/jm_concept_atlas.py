#!/usr/bin/env python3
"""
Concept Atlas — Jerry Maguire screenplay.
Model: claude-sonnet-4-5 via Anthropic (preferred) or gpt-4.1 via OpenAI (fallback).

Provenance field added to every record:
  provenance: "script_extraction"     — this pipeline
  provenance: "operator_reading"      — jm-c01..jm-c33 in CONCEPTS_JERRY_MCGUIRE_20261031.jsonl

Resume key: text_sha1.

Output: docs/jerry_mcguire_concepts/jm_atlas.jsonl
"""
import json, os, sys, re, time, random, hashlib, threading, queue
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent
SEGMENTS = ROOT / "tools" / "jm_segments.jsonl"
OUT      = ROOT / "docs" / "jerry_mcguire_concepts" / "jm_atlas.jsonl"
ENV_RUM  = ROOT / ".env"
ENV_SL   = ROOT.parent / "star_learning" / ".env"

# ── model / client ────────────────────────────────────────────────────────────
# Preferred: claude-sonnet-4-5 via Anthropic
# Fallback:  gpt-4.1 via OpenAI (same model the BeginningToNoww atlas used)
ANTHROPIC_MODEL = "claude-sonnet-4-5"
OPENAI_MODEL    = "gpt-4.1"

WORKERS      = 8
STAGGER_SEC  = 0.75
MAX_TOKENS   = 4096
MAX_ATTEMPTS = 3
SHUFFLE_SEED = 20261031


STARTER_CONCEPTS = [
    "Ambition", "Betrayal", "Commitment", "Communication", "Competition",
    "Complicity", "Confession", "Courage", "Cynicism", "Desire",
    "Failure", "Fame", "Family", "Friendship", "Grief",
    "Honesty", "Hope", "Identity", "Integrity", "Labour",
    "Love", "Loyalty", "Masculinity", "Money", "Morality",
    "Parenthood", "Redemption", "Sacrifice", "Speech", "Success",
    "Transformation", "Trust", "Vulnerability", "Witness"
]

PROMPT = """You are a precise concept extraction engine operating on a screenplay.

STARTER CONCEPTS (floor, not ceiling):
{starters}

For each block of screenplay text, extract ALL concepts present. For each concept:

1. DERIVE FROM ROOT FIRST — before naming, find the Aryan (PIE) or Scots-Gaelic root.
   Call it Aryan. If neither found, state none_found. Do not fabricate.

2. NAME the concept from the root outward. Precision means only enough and no more.

3. If you cannot match a concept to the starter list with semantic_concept_confidence > 0.7,
   MINT a new concept. Set minted: true. semantic_concept_confidence is confidence against
   the STARTER LIST, not in your mint. minted: true requires confidence < 0.7.

Output a JSON object with one key "concepts" containing an array. Each concept:
{{
  "concept_name": "string",
  "concept_name_in_context": "string — how the concept appears in THIS text.",
  "conceptual_understanding": "string — 2-4 sentences: definition, etymology, rationale.",
  "concept_root": {{
    "language": "Aryan | Scots-Gaelic | both | none_found",
    "derivation": "root → chain → concept_name"
  }},
  "semantic_concept_confidence": 0.0,
  "minted": false
}}

Screenplay text:
""".format(starters=", ".join(STARTER_CONCEPTS))


# ── cost tracking ─────────────────────────────────────────────────────────────
IN_PRICE_GPT   = 2.00  / 1_000_000
OUT_PRICE_GPT  = 8.00  / 1_000_000
IN_PRICE_ANT   = 3.00  / 1_000_000
OUT_PRICE_ANT  = 15.00 / 1_000_000

write_lock = threading.Lock()
stat_lock  = threading.Lock()
stats = {"cost": 0.0, "done": 0, "failed": 0}


def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()


def load_key(name):
    for env in (ENV_RUM, ENV_SL):
        if env.exists():
            for line in env.read_text().splitlines():
                line = line.strip()
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip()
    return os.environ.get(name, "")


def make_client():
    """Return (client, model, backend). Prefer Anthropic, fall back to OpenAI."""
    ant_key = load_key("ANTHROPIC_API_KEY")
    if ant_key:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=ant_key), ANTHROPIC_MODEL, "anthropic"
        except ImportError:
            pass

    oai_key = load_key("OPENAI_API_KEY")
    if oai_key:
        from openai import OpenAI
        return OpenAI(api_key=oai_key, max_retries=0), OPENAI_MODEL, "openai"

    print("No API key found (ANTHROPIC_API_KEY or OPENAI_API_KEY)", file=sys.stderr)
    sys.exit(1)


def extract_anthropic(client, model, text):
    msg = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": PROMPT + text}]
    )
    raw = msg.content[0].text
    data = json.loads(raw)
    concepts = data.get("concepts", data.get("concept", []))
    if isinstance(concepts, dict):
        concepts = [concepts]
    in_tok  = msg.usage.input_tokens
    out_tok = msg.usage.output_tokens
    cost = in_tok * IN_PRICE_ANT + out_tok * OUT_PRICE_ANT
    return concepts, cost


def extract_openai(client, model, text):
    resp = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": "You are a precise concept extraction engine. Output valid JSON only."},
            {"role": "user",   "content": PROMPT + text}
        ]
    )
    raw = resp.choices[0].message.content
    data = json.loads(raw)
    concepts = data.get("concepts", data.get("concept", []))
    if isinstance(concepts, dict):
        concepts = [concepts]
    u = resp.usage
    cost = u.prompt_tokens * IN_PRICE_GPT + u.completion_tokens * OUT_PRICE_GPT
    return concepts, cost


def load_segments():
    with SEGMENTS.open() as f:
        return [json.loads(l) for l in f if l.strip()]


def load_done():
    if not OUT.exists():
        return set()
    done = set()
    with OUT.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("provenance") == "script_extraction":
                    done.add(rec.get("text_sha1", ""))
            except Exception:
                pass
    return done


def worker(wid, client, model, backend, work, out_file, total):
    time.sleep(wid * STAGGER_SEC)
    while True:
        try:
            seg = work.get_nowait()
        except queue.Empty:
            return

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                if backend == "anthropic":
                    concepts, cost = extract_anthropic(client, model, seg["text"])
                else:
                    concepts, cost = extract_openai(client, model, seg["text"])

                record = {
                    "segment_id":    seg["segment_id"],
                    "scene_heading": seg.get("scene_heading", ""),
                    "text_sha1":     seg["text_sha1"],
                    "text":          seg["text"],
                    "concepts":      concepts,
                    "provenance":    "script_extraction",
                    "model":         model,
                }
                line = json.dumps(record) + "\n"
                with write_lock:
                    out_file.write(line)
                    out_file.flush()

                with stat_lock:
                    stats["cost"] += cost
                    stats["done"] += 1
                    n, cum = stats["done"], stats["cost"]

                minted = sum(1 for c in concepts if isinstance(c, dict) and c.get("minted"))
                print(f"  [t{wid:02d}] {seg['segment_id']}  {len(concepts)}c ({minted}m)  "
                      f"{n}/{total}  cum${cum:.3f}", flush=True)
                break

            except Exception as e:
                if attempt == MAX_ATTEMPTS:
                    with stat_lock:
                        stats["failed"] += 1
                    print(f"  [t{wid:02d}] FAIL {seg['segment_id']} attempt {attempt}: {e}",
                          file=sys.stderr, flush=True)
                else:
                    time.sleep(2 ** attempt + random.random())


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    client, model, backend = make_client()
    segments = load_segments()
    done     = load_done()
    todo     = [s for s in segments if s["text_sha1"] not in done]

    random.Random(SHUFFLE_SEED).shuffle(todo)

    print(f"Jerry Maguire Concept Atlas")
    print(f"  segments: {len(segments)} total, {len(done)} done, {len(todo)} to process")
    print(f"  model: {model} ({backend})  workers: {WORKERS}  seed: {SHUFFLE_SEED}")
    print(f"  output: {OUT}")

    if not todo:
        print("Nothing to do.")
        return

    work = queue.Queue()
    for seg in todo:
        work.put(seg)

    t0 = time.time()
    with OUT.open("a") as f:
        threads = [
            threading.Thread(
                target=worker,
                args=(i, client, model, backend, work, f, len(todo)),
                daemon=True
            )
            for i in range(WORKERS)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed/60:.1f} min  processed: {stats['done']}  "
          f"failed: {stats['failed']}  cost: ${stats['cost']:.3f}")


if __name__ == "__main__":
    main()

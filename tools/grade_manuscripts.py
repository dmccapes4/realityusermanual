#!/usr/bin/env python3
"""
grade_manuscripts.py — Grade each manuscript on a 5-axis rubric.
Uses the OpenAI API (or local .venv) to score each manuscript README/main doc.
Writes grades back to manuscripts/data.json.

Rubric axes (each 0-10):
  - Impact:     Field significance and originality
  - Rigor:      Methodological soundness or narrative logic
  - Clarity:    Prose quality and structure
  - Novelty:    Degree of new contribution
  - Coherence:  Internal consistency

Overall grade: weighted average → A/B/C/D letter.

Usage:
    .venv/bin/python tools/grade_manuscripts.py [--id plos-plume-wave] [--force]

Requires OPENAI_API_KEY in environment or .env file.
"""
import os, sys, json, pathlib, re, argparse, time

BASE = pathlib.Path(__file__).parent.parent
MS   = BASE / "manuscripts"
DATA = MS / "data.json"

AXES = ["Impact", "Rigor", "Clarity", "Novelty", "Coherence"]
AXIS_MAX = 10

def load_env():
    env_path = BASE / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))

def score_to_letter(avg):
    if avg >= 9.0: return "A+"
    if avg >= 8.5: return "A"
    if avg >= 8.0: return "A-"
    if avg >= 7.5: return "B+"
    if avg >= 7.0: return "B"
    if avg >= 6.5: return "B-"
    if avg >= 6.0: return "C+"
    if avg >= 5.5: return "C"
    if avg >= 5.0: return "C-"
    return "D"

def read_main_doc(ms):
    """Find and read the most representative document for a manuscript."""
    p = pathlib.Path(ms["path"])
    if not p.exists():
        return None, None
    # Priority: main manuscript md, readme, cover letter
    candidates = []
    for pattern in ["Main_Manuscript*.md", "README.md", "Cover_Letter*.md", "*.md"]:
        candidates.extend(sorted(p.glob(pattern)))
    if not candidates:
        return None, None
    doc = candidates[0]
    try:
        text = doc.read_text()[:6000]  # first 6000 chars
        return doc.name, text
    except:
        return None, None

def grade_with_openai(ms_name, doc_name, text, api_key):
    """Call OpenAI to grade the manuscript on the 5 axes. Returns dict."""
    import urllib.request, urllib.error

    prompt = f"""You are grading a manuscript on 5 axes, each scored 0-10.
Manuscript: {ms_name}
Source: {doc_name}

Text (first 6000 chars):
---
{text}
---

Score each axis 0-10 with one sentence justification.
Return ONLY valid JSON:
{{
  "axes": [
    {{"name": "Impact", "score": N, "max": 10, "note": "..."}},
    {{"name": "Rigor", "score": N, "max": 10, "note": "..."}},
    {{"name": "Clarity", "score": N, "max": 10, "note": "..."}},
    {{"name": "Novelty", "score": N, "max": 10, "note": "..."}},
    {{"name": "Coherence", "score": N, "max": 10, "note": "..."}}
  ],
  "summary": "2-3 sentence overall assessment"
}}"""

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 600,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload, method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    content = result["choices"][0]["message"]["content"]
    # Extract JSON
    m = re.search(r'\{[\s\S]*\}', content)
    if not m:
        raise ValueError(f"No JSON in response: {content[:200]}")
    return json.loads(m.group())

def grade_manuscript(ms, api_key, force=False):
    if ms.get("grade") and not force:
        print(f"  {ms['id']}: already graded (skip)")
        return ms

    doc_name, text = read_main_doc(ms)
    if not text:
        print(f"  {ms['id']}: no readable doc — skip")
        return ms

    print(f"  {ms['id']}: grading ({len(text)} chars)…", end="", flush=True)
    try:
        grade_data = grade_with_openai(ms["name"], doc_name, text, api_key)
        axes = grade_data.get("axes", [])
        avg = sum(a["score"] for a in axes) / len(axes) if axes else 5.0
        grade_data["overall"] = score_to_letter(avg)
        grade_data["avg"] = round(avg, 1)
        grade_data["date"] = "2026-10-29"
        ms["grade"] = grade_data
        print(f" ✓ {grade_data['overall']} ({avg:.1f}/10)")
    except Exception as e:
        print(f" ✗ {e}")
    time.sleep(0.5)
    return ms

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", help="Grade only this manuscript id")
    parser.add_argument("--force", action="store_true", help="Re-grade existing")
    args = parser.parse_args()

    load_env()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.")
        sys.exit(1)

    data = json.loads(DATA.read_text())
    manuscripts = data["manuscripts"]

    if args.id:
        manuscripts = [m for m in manuscripts if m["id"] == args.id]
        if not manuscripts:
            print(f"Not found: {args.id}")
            sys.exit(1)

    print(f"Grading {len(manuscripts)} manuscript(s)…")
    for ms in data["manuscripts"]:
        if args.id and ms["id"] != args.id:
            continue
        grade_manuscript(ms, api_key, force=args.force)

    DATA.write_text(json.dumps(data, indent=2))
    print(f"\ndata.json updated")

if __name__ == "__main__":
    main()

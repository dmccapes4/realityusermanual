"""Copy the book's exact wording into matching narration paragraphs.

For every paragraph the two files share (same words once emphasis, brackets and
case are ignored), the narration body is replaced by the book body, so emphasis
and punctuation are his. A paragraph is only replaced when the spoken key is
unchanged, so no existing audio is invalidated. Labels and cues are untouched.
"""
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_minus08_audio import key, spoken  # noqa: E402

BOOK = Path("quarantine/-08_book_pre_narration_20261107.md")
NARR = Path("src/phase2/-08.md")
LABEL = re.compile(r"^\*\*([^*]+?):\*\*\s*")


def norm(t):
    t = re.sub(r"[*_>()\[\]]", "", t).replace("’", "'")
    return re.sub(r"\s+", " ", t).strip().lower().rstrip(".")


def book_paras():
    out = []
    for p in BOOK.read_text().split("\n\n"):
        s = p.strip()
        if not s or s.startswith(("#", "---", "~~", "```")):
            continue
        out.append(LABEL.sub("", s, count=1))
    return out


def narr_paras(lines):
    """(body_start, body_end, body) for each spoken paragraph in the narration."""
    out, i = [], 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].strip():
            j += 1
        block = [k for k in range(i, j) if not lines[k].startswith("~~")]
        if block and not lines[block[0]].startswith(("#", "---", "```")):
            first = block[0]
            m = LABEL.match(lines[first])
            if m and lines[first][m.end():].strip() == "" and len(block) > 1:
                body_idx = block[1:]
            elif m:
                body_idx = block
            else:
                body_idx = block
            body = "\n".join(lines[k] for k in body_idx)
            body = LABEL.sub("", body, count=1) if m and body_idx[0] == first else body
            out.append((body_idx, body))
        i = j
    return out


def main():
    lines = NARR.read_text().split("\n")
    B = book_paras()
    N = narr_paras(lines)
    sm = difflib.SequenceMatcher(None, [norm(b) for b in B], [norm(n[1]) for n in N], autojunk=False)
    changed = skipped = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            continue
        for b, (idx, body) in zip(B[i1:i2], N[j1:j2]):
            if b == body or "\n" in b or "\n" in body:
                continue
            if key(spoken(b)) != key(spoken(body)):
                skipped += 1
                print("SKIP", body[:90])
                continue
            first = idx[0]
            m = LABEL.match(lines[first])
            prefix = lines[first][: m.end()] if m and len(idx) == 1 else ""
            lines[first] = prefix + b
            changed += 1
    NARR.write_text("\n".join(lines))
    print(f"replaced {changed}, skipped {skipped}")


if __name__ == "__main__":
    main()

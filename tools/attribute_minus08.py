"""One-shot attribution pass for src/phase2/-08.md.

Unlabeled narration becomes **Narrator:**, Lisbeth's reader translations become
**Lisbeth (English):**. Code listings, the header, sound effects, the goat note,
the party's unattributed sentence and the closing Axiomite block are left alone.
"""
import re
import sys

PATH = "src/phase2/-08.md"

LISBETH_EN = (
    "*I like that the rules", "*I agree with your frustration", "*Witches cackle.",
    "*No.*", "*I disagree with being told", "*Njála goes ahead up", "*Njála climbs.",
    "*I will let a coin spin", "*Yield is not surrender", "*Shut up, you dickface",
    "*She does not whisper words to him", "*Search the scope", "*Rescue. Leader.",
    "*Twenty-eight.*", "*There is ground on the top", "*The patient is under the knife",
    "*The GM gave away", "*Is it moral to hoard", "*The river winds",
    "*That is consequent handelen.*", "*Draavio would have taken a note",
    "*Without his meticulous", "*What defines commitment", "*Draavio would say that bureaucracy",
    "*Geometry is just expression", "*Consequent handelen.*", "*I will be hiding",
    "*Commitment does not require", "*It says: where it is laid out", "*No. Draavio continued",
    "*Hold on. She knows.", "*Full attack.*", "*The claws. The fucking claws",
    "*The iguana does the looks", "*Read.*", "*The goat carries what others did",
)
NARRATOR_EN = (
    "*The Narrator feels that her speech is best transformed",
    "*Njála has no actions this round.",
    "*The kernel has been running since the climb.",
)
ARCHIVIST = (
    "*Ekrupsen toe argurion.*", "*Auto.* Just that?", "Matthew exposed the lies",
    "Exactly there. The expression. That. He points",
)
LEAVE = (
    "*A coin with two sides.", "*Arrays A and B", "*Each cycle:*",
    "*\"I have to go see about a goat.\"*", "*Beware.*", "*Beware. Not the outer shell",
)
CLICK = re.compile(r"^\*'click'[^*]*\*$")


def unwrap(text):
    """Remove whole-paragraph italics, turning inner toggles into emphasis."""
    if not (text.startswith("*") and not text.startswith("**") and text.endswith("*")
            and not text.endswith("**")):
        return text
    inner = text[1:-1]
    parts = inner.split("*")
    if len(parts) % 2 == 0:
        sys.exit(f"unbalanced italics: {text[:80]}")
    out = []
    for i, seg in enumerate(parts):
        if i % 2 == 0:
            out.append(seg)
        else:
            lead = seg[: len(seg) - len(seg.lstrip())]
            trail = seg[len(seg.rstrip()):]
            out.append(f"{lead}*{seg.strip()}*{trail}")
    return "".join(out)


def main():
    src = open(PATH).read().split("\n")
    end = next(i for i, l in enumerate(src) if l.startswith("**Sheldon:** Daemons are outsiders"))
    out, i = [], 0
    in_fence = in_coda = False
    while i < len(src):
        line = src[i]
        s = line.strip()
        if i < 36 or i >= end:
            out.append(line); i += 1; continue
        if s.startswith("```"):
            in_fence = not in_fence
        if s == '"""':
            in_coda = not in_coda
        if in_fence or in_coda or s.startswith("```") or s == '"""' or not s:
            out.append(line); i += 1; continue
        j = i
        while j < len(src) and src[j].strip():
            j += 1
        para = src[i:j]
        first = para[0].strip()
        if (re.match(r"^\*\*[^*]+?:\*\*", first) or first.startswith(("#", "---", ">", "|", "~~", "**Doctor Drake**"))
                or re.match(r"^\*\([^)]*\)\*$", first) or CLICK.match(first)
                or first.startswith(LEAVE) or re.match(r"^\*\d+\. ", first)):
            if first.startswith("**Lisbeth:** *(she does not write;"):
                note = first[len("**Lisbeth:** *("):-2]
                para = ["**Narrator:** " + note[0].upper() + note[1:] + "."]
            out.extend(para); i = j; continue
        if first.startswith("That. One. On the other hand."):
            out.append("**Lisbeth:** " + first); i = j; continue
        if first == "Scape.":
            out.append("**Archivist:** Scape."); i = j; continue
        if first.startswith("*The river winds"):
            body = [l.strip().strip("*") for l in para]
            out.append("**Lisbeth (English):**")
            out.append("")
            out.extend("> " + b for b in body)
            i = j; continue
        if len(para) > 1:
            body = [unwrap(l.strip()) for l in para]
            out.append("**Narrator:** " + body[0])
            out.extend(body[1:])
            i = j; continue
        if first.startswith(LISBETH_EN):
            label = "Lisbeth (English)"
        elif first.startswith(NARRATOR_EN):
            label = "Narrator (English)"
        elif first.startswith(ARCHIVIST):
            label = "Archivist"
        else:
            label = "Narrator"
        out.append(f"**{label}:** " + unwrap(first))
        i = j
    open(PATH, "w").write("\n".join(out))


if __name__ == "__main__":
    main()

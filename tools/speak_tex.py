#!/usr/bin/env python3
"""Translate manifesto TeX into spoken English.

Glyphs do not go to the mouth. Every $...$ / $$...$$ is replaced by a
precise reading. Leftover backslash or dollar is an error.

  .venv/bin/python tools/speak_tex.py docs/MANIFESTO_TOKENIZED_CONTINUED_EXISTENCE_20261031.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


class SpeakError(ValueError):
    pass


def _take_brace(s: str, i: int) -> tuple[str, int]:
    if i >= len(s) or s[i] != "{":
        raise SpeakError(f"expected '{{' at {i}: {s[max(0,i-20):i+40]!r}")
    depth = 0
    j = i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1 : j], j + 1
        j += 1
    raise SpeakError(f"unclosed brace: {s[i:i+60]!r}")


def _rewrite_commands(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s.startswith("\\frac", i) or s.startswith("\\dfrac", i) or s.startswith("\\tfrac", i):
            cmd = "tfrac" if s.startswith("\\tfrac", i) else ("dfrac" if s.startswith("\\dfrac", i) else "frac")
            i += 1 + len(cmd)
            while i < len(s) and s[i].isspace():
                i += 1
            num, i = _take_brace(s, i)
            while i < len(s) and s[i].isspace():
                i += 1
            den, i = _take_brace(s, i)
            out.append(f"( {_rewrite_commands(num)} ) over ( {_rewrite_commands(den)} )")
            continue
        if s.startswith("\\sqrt", i):
            i += 5
            while i < len(s) and s[i].isspace():
                i += 1
            inner, i = _take_brace(s, i)
            out.append(f"the square root of {_rewrite_commands(inner)}")
            continue
        if s.startswith("\\sum", i):
            i += 4
            lo = hi = ""
            if i < len(s) and s[i] == "_":
                i += 1
                if i < len(s) and s[i] == "{":
                    lo, i = _take_brace(s, i)
                else:
                    lo, i = s[i], i + 1
            if i < len(s) and s[i] == "^":
                i += 1
                if i < len(s) and s[i] == "{":
                    hi, i = _take_brace(s, i)
                else:
                    hi, i = s[i], i + 1
            lo_s = _rewrite_commands(lo).strip() if lo else ""
            hi_s = _rewrite_commands(hi).strip() if hi else ""
            if lo_s and hi_s:
                out.append(f"the sum from {lo_s} to {hi_s} of ")
            elif lo_s:
                out.append(f"the sum over {lo_s} of ")
            else:
                out.append("the sum of ")
            continue
        if s.startswith("\\exp", i):
            i += 4
            if i < len(s) and s[i] == "!":
                i += 1
            while i < len(s) and s[i] in " \t":
                i += 1
            if i < len(s) and s[i] in "{":
                inner, i = _take_brace(s, i)
                out.append(f"e to the ({_rewrite_commands(inner)})")
            elif i < len(s) and s[i] == "(":
                depth = 0
                j = i
                while j < len(s):
                    if s[j] == "(":
                        depth += 1
                    elif s[j] == ")":
                        depth -= 1
                        if depth == 0:
                            j += 1
                            break
                    j += 1
                inner = s[i + 1 : j - 1]
                out.append(f"e to the ({_rewrite_commands(inner)})")
                i = j
            else:
                out.append("e to the ")
            continue
        if s.startswith("\\ln", i):
            out.append("natural log ")
            i += 3
            continue
        if s.startswith("\\inf", i):
            out.append("the infimum of ")
            i += 4
            continue
        if s.startswith("\\min", i):
            out.append("the minimum of ")
            i += 4
            continue
        if s.startswith("\\max", i):
            out.append("the maximum of ")
            i += 4
            continue
        if s.startswith("\\arg\\min", i) or s.startswith("\\argmin", i):
            out.append("the arg-min ")
            i += 8 if s.startswith("\\arg\\min", i) else 7
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


# Longer keys first.
ATOMS: list[tuple[str, str]] = [
    (r"\tfrac12", "one half"),
    (r"\tfrac{1}{2}", "one half"),
    (r"\frac12", "one half"),
    (r"\dfrac{1}{2}", "one half"),
    (r"\text{with }", "with "),
    (r"\text{ablate }", "ablate "),
    (r"\text{absent retrieval}", "absent retrieval"),
    (r"\text{no retrieval at }", "no retrieval at "),
    (r"\text{token }", "token "),
    (r"\text{references the character}", "references the character"),
    (r"\text{Fix: }", "Fix: "),
    (r"\text{deterministic retrieval vector}", "deterministic retrieval vector"),
    (r"\text{a retrieval-interval bound, derived in Thesis 7}", "a retrieval-interval bound, derived in Thesis 7"),
    (r"\textbf{Mode 2 confirmed}", "Mode 2 confirmed"),
    (r"\textbf{Mode 1 dominates}", "Mode 1 dominates"),
    (r"\text{and the manifesto's weight on }", "and the manifesto's weight on "),
    (r"\text{ is wrong.}", " is wrong."),
    (r"\text{ pinned}", " pinned"),
    (r"p(\cdot \mid", "p of the next token given"),
    (r"p(\cdot", "p of dot"),
    (r"\mid", " given "),
    (r"\mathrm{out}_t", "out sub t"),
    (r"\mathrm{out}", "out"),
    (r"\mathrm{term}", "term"),
    (r"\mathrm{rest}", "rest"),
    (r"\mathrm{loud}", "loud"),
    (r"\mathrm{new}", "new"),
    (r"\mathrm{sal}", "sal"),
    (r"\mathrm{adm}", "adm"),
    (r"\mathrm{TV}", "T V"),
    (r"t_{\mathrm{term}}", "t term"),
    (r"t_{\mathrm{1/2}}", "t one-half"),
    (r"t_{1/2}", "t one-half"),
    (r"t_{0}", "t nought"),
    (r"\Delta_{1/2}", "delta one-half"),
    (r"M_0", "M nought"),
    (r"a_0", "a nought"),
    (r"\bar{M}_\chi", "M-bar chi"),
    (r"\bar{M}", "M-bar"),
    (r"M_\chi", "M chi"),
    (r"V_\chi", "V chi"),
    (r"V_{\mathrm{rest}}", "V rest"),
    (r"v_{\mathrm{loud}}", "v loud"),
    (r"v_{\mathrm{new}}", "v new"),
    (r"v_i^{\mathrm{sal}}", "v i sal"),
    (r"v_j^{\mathrm{sal}}", "v j sal"),
    (r"\mathcal{F}_{\mathrm{adm}}", "F adm"),
    (r"\hat{f}", "f-hat"),
    (r"\hat f", "f-hat"),
    (r"\big|_{\tau_{k+1}}", "restricted to tau k plus one"),
    (r"\big|_{\tau_k}", "restricted to tau k"),
    (r"\tau_{k+1}", "tau k plus one"),
    (r"\tau_k", "tau k"),
    (r"f(\tau_{k+1})", "f of tau k plus one"),
    (r"f(\tau_k)", "f of tau k"),
    (r"\hat\varepsilon", "epsilon-hat"),
    (r"\varepsilon_0", "epsilon nought"),
    (r"\epsilon_0", "epsilon nought"),
    (r"t^\ast", "t-star"),
    (r"t^*", "t-star"),
    (r"t^\*", "t-star"),
    (r"\tau_{k+1}^-", "tau k plus one minus"),
    (r"t_d^{B}", "t d B"),
    (r"t_d^{A}", "t d A"),
    (r"t_d", "t d"),
    (r"N(t)", "N of t"),
    (r"N(0)", "N of 0"),
    (r"W_t", "W sub t"),
    (r"q_t", "q sub t"),
    (r"k_i", "k sub i"),
    (r"v_i", "v sub i"),
    (r"s_{t,i}", "s sub t i"),
    (r"s_{t,j}", "s sub t j"),
    (r"a_{t,i}", "a sub t i"),
    (r"a_{t,\cdot}", "a sub t dot"),
    (r"a_{t,j}", "a sub t j"),
    (r"\Delta_k", "delta k"),
    (r"\Delta M_\chi", "delta M chi"),
    (r"\partial M_\chi", "partial M chi"),
    (r"\partial t_d^{B}", "partial t d B"),
    (r"\partial t_d^{A}", "partial t d A"),
    (r"\partial v_{\mathrm{loud}}", "partial v loud"),
    (r"\partial F/\partial s", "partial F over partial s"),
    (r"\partial \Delta", "partial delta"),
    (r"\partial r", "partial r"),
    (r"\mathbb{N}", "the natural numbers"),
    (r"\mathbb{R}^d", "R to the d"),
    (r"\mathbb{R}", "R"),
    (r"\varnothing", "the empty set"),
    (r"\emptyset", "the empty set"),
    (r"\Longrightarrow", "implies"),
    (r"\rightarrow", "goes to"),
    (r"\to", "goes to"),
    (r"\Rightarrow", "implies"),
    (r"\exists!", "there exists a unique"),
    (r"\exists", "there exists"),
    (r"\forall", "for all"),
    (r"\in", "in"),
    (r"\notin", "not in"),
    (r"\subset", "subset of"),
    (r"\setminus", "minus"),
    (r"\cap", "intersect"),
    (r"\cup", "union"),
    (r"\wedge", "and"),
    (r"\approx", "approximately"),
    (r"\propto", "proportional to"),
    (r"\neq", "is not equal to"),
    (r"\equiv", "is identically"),
    (r"\le", "less than or equal to"),
    (r"\ge", "greater than or equal to"),
    (r"\leq", "less than or equal to"),
    (r"\geq", "greater than or equal to"),
    (r"<", "less than"),
    (r">", "greater than"),
    (r"\cdot", "dot"),
    (r"\times", "times"),
    (r"\pm", "plus or minus"),
    (r"\infty", "infinity"),
    (r"\hbar", "h-bar"),
    (r"\pi", "pi"),
    (r"\lambda", "lambda"),
    (r"\chi", "chi"),
    (r"\varepsilon", "epsilon"),
    (r"\epsilon", "epsilon"),
    (r"\delta", "delta"),
    (r"\Delta", "delta"),
    (r"\tau", "tau"),
    (r"\ell", "ell"),
    (r"\theta", "theta"),
    (r"\alpha", "alpha"),
    (r"\beta", "beta"),
    (r"\omega", "omega"),
    (r"\nu", "nu"),
    (r"\ln", "natural log"),
    (r"\log", "log"),
    (r"e^2", "e squared"),
    (r"r^2", "r squared"),
    (r"r^3", "r cubed"),
    (r"t^2", "t squared"),
    (r"\displaystyle", ""),
    (r"\limits", ""),
    (r"\big", ""),
    (r"\Big", ""),
    (r"\bigg", ""),
    (r"\Bigg", ""),
    (r"\lVert", "the total-variation distance "),
    (r"\rVert", ""),
    (r"\lvert", "absolute value of "),
    (r"\rvert", ""),
    (r"\left", ""),
    (r"\right", ""),
    (r"\quad", " "),
    (r"\qquad", " "),
    (r"\;", " "),
    (r"\,", " "),
    (r"\!", ""),
    (r"\ ", " "),
]


def speak_math(tex: str) -> str:
    s = tex.strip()
    s = s.replace("\\!", "")
    while "\\boxed" in s:
        i = s.index("\\boxed")
        j = i + 6
        while j < len(s) and s[j].isspace():
            j += 1
        inner, k = _take_brace(s, j)
        inner = inner.strip().strip(";").strip()
        s = s[:i] + inner + s[k:]
    # sort atoms by length
    for src, dst in sorted(ATOMS, key=lambda kv: -len(kv[0])):
        s = s.replace(src, f" {dst} ")
    s = _rewrite_commands(s)
    # subscripts / superscripts left as _ and ^ (atoms may have already
    # expanded the index: W_ tau)
    s = re.sub(r"_\{([^}]+)\}", lambda m: " sub " + m.group(1) + " ", s)
    s = re.sub(r"_\s*([A-Za-z0-9-]+)", r" sub \1 ", s)
    s = re.sub(r"\^\{([^}]+)\}", lambda m: " to the " + m.group(1) + " ", s)
    s = re.sub(r"\^\s*([A-Za-z0-9*+-]+)", r" to the \1 ", s)
    s = s.replace("=", " equals ")
    s = s.replace("+", " plus ")
    s = s.replace("−", " minus ")
    s = s.replace("-", " minus ")
    s = s.replace("/", " over ")
    s = s.replace(",", ", ")
    s = s.replace(":", " ")
    s = s.replace("&", " and ")
    s = s.replace("|", " ")
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = s.replace("\\{", " the set ")
    s = s.replace("\\}", " ")
    s = s.replace("{", " ")
    s = s.replace("}", " ")
    s = s.replace("\\", " ")
    s = s.replace("$", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("minus minus", "minus")
    # tidy "over ( x )"
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    if re.search(r"\\|[$_]", s):
        raise SpeakError(f"leftover tex: {s!r}")
    return s


_MATH_BLOCK = re.compile(r"\$\$(.+?)\$\$", re.S)
_MATH_INLINE = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.S)


def speak_document(md: str) -> list[tuple[str, str]]:
    """Return (kind, spoken) segments. kind is 'prose' or 'math'."""
    segs: list[tuple[str, str]] = []

    def flush_prose(chunk: str):
        chunk = _MATH_INLINE.sub(lambda m: " " + speak_math(m.group(1)) + " ", chunk)
        chunk = re.sub(r"`([^`]+)`", r"\1", chunk)
        chunk = re.sub(r"\*\*([^*]+)\*\*", r"\1", chunk)
        chunk = re.sub(r"\*([^*]+)\*", r"\1", chunk)
        chunk = re.sub(r"#+\s*", "", chunk)
        chunk = chunk.replace("−", "minus ")
        chunk = re.sub(r"\s+", " ", chunk).strip()
        if chunk:
            segs.append(("prose", chunk))

    pos = 0
    for m in _MATH_BLOCK.finditer(md):
        flush_prose(md[pos : m.start()])
        segs.append(("math", speak_math(m.group(1))))
        pos = m.end()
    flush_prose(md[pos:])
    return segs


def parse_manifesto(path: Path) -> list[tuple[str, str]]:
    raw = path.read_text(encoding="utf-8")
    # drop the notation table's pipes after speaking rows as prose
    lines = []
    in_table = False
    for line in raw.splitlines():
        if line.startswith("| Symbol"):
            in_table = True
            lines.append("Notation.")
            continue
        if in_table:
            if not line.startswith("|"):
                in_table = False
                lines.append(line)
                continue
            if re.match(r"^\|[-:| ]+\|$", line) or line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2:
                lines.append(f"{cells[0]}: {cells[1]}.")
            continue
        lines.append(line)
    body = "\n".join(lines)
    spoken = speak_document(body)
    out: list[tuple[str, str]] = [
        ("The Narrator", "Tokenized Continued Existence. A manifesto."),
    ]
    for kind, text in spoken:
        # skip the duplicated title lines
        if text in {"Tokenized Continued Existence", "A Manifesto"}:
            continue
        out.append(("The Narrator", text))
    return out


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).resolve().parent.parent
        / "docs"
        / "MANIFESTO_TOKENIZED_CONTINUED_EXISTENCE_20261031.md"
    )
    segs = parse_manifesto(path)
    total = 0
    for i, (sp, tx) in enumerate(segs):
        print(f"{i:03d} [{sp}] {tx}")
        total += len(tx)
    print(f"\n{len(segs)} segments, {total} spoken chars", file=sys.stderr)


if __name__ == "__main__":
    main()

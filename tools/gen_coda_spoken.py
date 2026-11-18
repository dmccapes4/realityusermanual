#!/usr/bin/env python3
"""
gen_coda_spoken.py
Reads truth/coda.c line by line and produces a spoken-aloud narration script.
Every symbol is named. Every identifier's underscores are spoken.
Output: one plain-English line per C source line, printed to stdout.
"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC  = BASE / "truth" / "coda.c"

# ── Identifier map (whole-word, longest first to avoid prefix shadowing) ──────
IDENTS = [
    ("rotate_address_space",  "rotate address space"),
    ("node_write_next",       "node write next"),
    ("presence_check",        "presence check"),
    ("secrets_read",          "secrets read"),
    ("secrets_write",         "secrets write"),
    ("list_traverse",         "list traverse"),
    ("clock_gettime",         "clock gettime"),
    ("iso8601",               "ISO eight six oh one"),
    ("log_line",              "log line"),
    ("node_read",             "node read"),
    ("new_a_head",            "new a head"),
    ("new_b_head",            "new b head"),
    ("new_order",             "new order"),
    ("skip_count",            "skip count"),
    ("skip_idx",              "skip idx"),
    ("node_off",              "node off"),
    ("coin_before",           "coin before"),
    ("t_start",               "t start"),
    ("t_end",                 "t end"),
    ("tv_sec",                "tv sec"),
    ("tv_nsec",               "tv nsec"),
    ("src_n",                 "src n"),
    ("dst_n",                 "dst n"),
    ("term_00",               "term zero zero"),
    ("term_01",               "term zero one"),
    ("term_10",               "term one zero"),
    ("term_11",               "term one one"),
    ("a_head",                "a head"),
    ("b_head",                "b head"),
    ("a_bytes",               "a bytes"),
    ("b_bytes",               "b bytes"),
    ("a_off",                 "a off"),
    ("b_off",                 "b off"),
    ("a_dat",                 "a dat"),
    ("b_dat",                 "b dat"),
    ("b_base",                "b base"),
    ("skip_idx",              "skip idx"),
    ("UINT64_MAX",            "YEWINT sixty-four MAX"),
    ("uint64_t",              "yew-int sixty-four t"),
    ("uint8_t",               "yew-int eight t"),
    ("size_t",                "size t"),
    ("MAX_N",                 "MAX N"),
    ("NO_NEXT",               "NO NEXT"),
    ("NODE_SIZE",             "NODE SIZE"),
    ("PATH_DAT",              "PATH DAT"),
    ("PATH_SEC",              "PATH SEC"),
    ("PATH_LOG",              "PATH LOG"),
    ("PATH_SRC",              "PATH SRC"),
    ("PATH_EXE",              "PATH EXE"),
    ("CC_CMD",                "CC CMD"),
    ("CLOCK_MONOTONIC",       "CLOCK MONOTONIC"),
    ("SEEK_SET",              "SEEK SET"),
    ("timespec",              "timespec"),
    ("typedef",               "type def"),
    ("struct",                "struct"),
    ("static",                "static"),
    ("const",                 "const"),
    ("void",                  "void"),
    ("int",                   "int"),
    ("long",                  "long"),
    ("double",                "double"),
    ("float",                 "float"),
    ("char",                  "char"),
    ("FILE",                  "FILE"),
    ("NULL",                  "NULL"),
    ("exit",                  "exit"),
    ("return",                "return"),
    ("while",                 "while"),
    ("for",                   "for"),
    ("if",                    "if"),
    ("else",                  "else"),
    ("break",                 "break"),
    ("continue",              "continue"),
    ("fseek",                 "fseek"),
    ("fread",                 "fread"),
    ("fwrite",                "fwrite"),
    ("fopen",                 "fopen"),
    ("fclose",                "fclose"),
    ("fflush",                "fflush"),
    ("fprintf",               "fprintf"),
    ("printf",                "printf"),
    ("snprintf",              "snprintf"),
    ("perror",                "perror"),
    ("strftime",              "strftime"),
    ("gmtime",                "gmtime"),
    ("system",                "system"),
    ("unlink",                "unlink"),
    ("sleep",                 "sleep"),
    ("execv",                 "execv"),
    ("round",                 "round"),
    ("ceil",                  "ceil"),
    ("sqrt",                  "sqrt"),
    ("puts",                  "puts"),
    ("time",                  "time"),
    ("main",                  "main"),
    ("init",                  "init"),
]

INCLUDES = {
    "<stdio.h>":   "left-arrow stdio dot h right-arrow",
    "<stdlib.h>":  "left-arrow stdlib dot h right-arrow",
    "<stdint.h>":  "left-arrow stdint dot h right-arrow",
    "<string.h>":  "left-arrow string dot h right-arrow",
    "<math.h>":    "left-arrow math dot h right-arrow",
    "<time.h>":    "left-arrow time dot h right-arrow",
    "<unistd.h>":  "left-arrow unistd dot h right-arrow",
}


def apply_idents(s: str) -> str:
    for src, dst in IDENTS:
        s = re.sub(r'\b' + re.escape(src) + r'\b', dst, s)
    return s


def sanitize_strings(s: str) -> str:
    """Replace the contents of C string literals with spoken equivalents."""
    # Handle >> prefix in puts strings: ">>" → "double-arrow"
    s = re.sub(r'"(>>)\s', r'"double-arrow ', s)
    # Escape sequences inside strings
    s = s.replace(r'\"', 'quote ')
    s = s.replace(r'\n', ' backslash-n ')
    s = s.replace(r'\t', ' backslash-t ')
    # printf format specifiers
    s = s.replace('%s',   'percent-s')
    s = s.replace('%d',   'percent-d')
    s = s.replace('%llu', 'percent-llu')
    s = s.replace('%lld', 'percent-lld')
    s = s.replace('%.3f', 'percent-dot-three-f')
    s = s.replace('%.1f', 'percent-dot-one-f')
    s = s.replace('%d',   'percent-d')
    # File paths inside strings
    s = re.sub(r'truth/(\w+)\.(\w+)', lambda m: f'truth slash {m.group(1)} dot {m.group(2)}', s)
    s = re.sub(r'truth/(\w+)', r'truth slash \1', s)
    # Remove outer quote marks from string literals (they're implicit in context)
    return s


def apply_operators(s: str) -> str:
    # Multi-char first
    s = s.replace("->",  " arrow ")
    s = s.replace("==",  " double-equals ")
    s = s.replace("!=",  " not-equals ")
    s = s.replace("^=",  " XOR-equals ")
    s = s.replace("+=",  " plus-equals ")
    s = s.replace("-=",  " minus-equals ")
    s = s.replace("*=",  " times-equals ")
    s = s.replace("<=",  " less-or-equal ")
    s = s.replace(">=",  " greater-or-equal ")
    s = s.replace("<<",  " left-shift ")
    s = s.replace(">>",  " double-arrow ")
    s = s.replace("++",  " plus-plus ")
    s = s.replace("--",  " minus-minus ")
    s = s.replace("&&",  " and ")
    s = s.replace("||",  " or ")
    s = s.replace(">",   " greater-than ")
    s = s.replace("<",   " less-than ")
    s = s.replace("$",   " dollar ")
    s = s.replace("/",   " slash ")
    # Pointer/address-of: & before identifier
    s = re.sub(r'&(\w)', r' ampersand \1', s)
    # Pointer star: * before identifier or after type
    s = re.sub(r'\*(\w)', r' star \1', s)
    # Single-char
    s = s.replace("{",   " open-brace ")
    s = s.replace("}",   " close-brace ")
    s = s.replace("(",   " open-paren ")
    s = s.replace(")",   " close-paren ")
    s = s.replace("[",   " open-bracket ")
    s = s.replace("]",   " close-bracket ")
    s = s.replace(",",   " comma ")
    s = s.replace(";",   " semicolon")
    s = s.replace("_",   " underscore ")
    # Degree symbol
    s = s.replace("°",   " degrees ")
    # Remaining slashes in paths (not comment markers already replaced)
    s = re.sub(r'(?<![a-z])/(?=[a-z])', ' slash ', s)
    return s


def clean(s: str) -> str:
    # Collapse multiple spaces
    s = re.sub(r'  +', ' ', s)
    return s.strip()


def process_comment_line(s: str) -> str:
    """Handle a line that is part of a block comment."""
    # Strip leading ' * ' or ' *'
    s = re.sub(r'^\s*\*\s?', '', s)
    # If it's just the closing */
    if s.strip() == '/':
        return "star forward-slash"
    return s.strip()


def indent_word(level: int) -> str:
    if level == 0: return ""
    if level == 1: return "indent "
    if level == 2: return "double-indent "
    return "triple-indent "


def process_line(raw: str) -> str | None:
    line = raw.rstrip("\n")

    # Blank
    if not line.strip():
        return None

    # Decorative separator (═══ or ===)
    if re.match(r'^\s*[/*\s]*[═=]{8,}', line):
        return None

    stripped = line.lstrip()
    indent = len(line) - len(stripped)
    level  = indent // 4
    pfx    = indent_word(level)

    # ── Block comment start/end ──────────────────────────────────────────────
    # Line is a full block comment: /* ... */
    if stripped.startswith("/*") and stripped.endswith("*/"):
        inner = stripped[2:-2].strip()
        if not inner:
            return None
        return pfx + "forward-slash star " + inner + " star forward-slash"

    # Opening /* (no closing on same line)
    if stripped.startswith("/*"):
        inner = stripped[2:].strip()
        return pfx + "forward-slash star " + inner

    # Closing */
    if stripped.startswith("*/") or stripped == "*/":
        return pfx + "star forward-slash"

    # Continuation line inside block comment
    if stripped.startswith("* ") or stripped == "*":
        inner = stripped[1:].strip()
        if not inner:
            return None
        return pfx + "star " + inner

    # ── Hash comment (awk, shell). #include / #define stay below. ──
    if stripped.startswith("#") and not stripped.startswith(("#include", "#define")):
        rest = stripped[1:].strip()
        rest = apply_idents(rest)
        rest = apply_operators(rest)
        return clean(pfx + "hash " + rest)

    # ── Preprocessor ─────────────────────────────────────────────────────────
    if stripped.startswith("#include"):
        rest = stripped[len("#include"):].strip()
        spoken = INCLUDES.get(rest, rest)
        return pfx + "hashtag include " + spoken

    if stripped.startswith("#define"):
        rest = stripped[len("#define"):].strip()
        rest = apply_idents(rest)
        rest = apply_operators(rest)
        return pfx + "hashtag define " + clean(rest)

    # ── Normal code line ─────────────────────────────────────────────────────
    # Strip inline // comment (we'll re-attach spoken)
    inline_comment = ""
    if "//" in stripped:
        idx = stripped.index("//")
        inline_comment = " slash-slash " + stripped[idx+2:].strip()
        stripped = stripped[:idx].rstrip()

    # Strip inline /* comment */
    def strip_inline_block(s: str) -> tuple[str, str]:
        m = re.search(r'/\*(.+?)\*/', s)
        if not m:
            return s, ""
        comment = " forward-slash star " + m.group(1).strip() + " star forward-slash"
        code = s[:m.start()] + s[m.end():]
        return code.strip(), comment

    stripped, block_comment = strip_inline_block(stripped)

    # Sanitize string literal contents first
    s = sanitize_strings(stripped)
    # Apply identifier substitutions (whole-word)
    s = apply_idents(s)
    # Apply operators and punctuation
    s = apply_operators(s)
    s = clean(s)

    result = pfx + s + block_comment + inline_comment
    result = clean(result)
    if not result:
        return None
    return result


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    out = []
    for raw in lines:
        spoken = process_line(raw)
        if spoken:
            out.append(spoken)
    print("\n".join(out))


if __name__ == "__main__":
    main()

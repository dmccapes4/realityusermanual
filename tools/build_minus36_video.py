#!/usr/bin/env python3
"""Build Page -36 — The   Bed.

Operator recordings remain untouched:
  HiFrances.m4a -> Explorer montage
  HiJuju.m4a    -> Kangaroo Park bones / Unity animals
  TheBed.m4a    -> Zecliptic angle flight into Sol

Matilda narrates only the rendered/unrendered and technical examination.

Usage:
  .venv/bin/python tools/build_minus36_video.py audio
  .venv/bin/python tools/build_minus36_video.py assemble
  .venv/bin/python tools/build_minus36_video.py all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
DEV = BASE.parent
STAR = DEV / "star_learning"
OUT = BASE / "video" / "minus36"
WORK = OUT / "work"
STILLS = OUT / "stills"
AUDIO = BASE / "audio" / "minus36"
SEGMENTS = AUDIO / "segments"
FINAL = OUT / "-36_the_bed.mp4"

W, H, FPS = 1280, 720, 30
MATILDA = os.environ.get("VOICE_MATILDA", "XrExE9yKIg1WjnnlVkGX")
ELEVEN = "https://api.elevenlabs.io/v1"
VOICE_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True,
    "speed": 0.92,
}

_env = BASE / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def _n(title: str, text: str, screen: list[str]) -> dict:
    return {"title": title, "text": text.strip(), "screen": screen}


NARRATION = [
    _n(
        "THE TIP OF THE ICEBERG",
        """
        One term before the examination. The human author is called the
        operator, and the A I collaborators are agents. Literal filesystem
        strings keep their exact spelling.

        The seven spoken lines were the content beneath print. They were not
        the whole program that made the content print. Pull back and the poem
        becomes a file claimed at once by shell, Python, C, and Markdown. No
        one parser receives the whole. The reading was the visible tip; the
        software beneath it is the rest of the poem.
        """,
        [
            "#!/bin/bash",
            "# still_yet_unarrived.c",
            "",
            "the operator = human author",
            "agents = AI collaborators",
            "literal paths retain literal names",
            "",
            "import family # loads module dynamically",
            "# include <self>",
            "uint main(void) {",
            "    print:",
            "    ...",
            "}",
            "return 0;",
            "```  terminal poem  ```",
        ],
    ),
    _n(
        "UNRENDERED / RENDERED",
        """
        The poem has two coequal presentations and recommends neither. In the
        unrendered source, every hash, escape, backtick, indentation level,
        prompt, and space remains inspectable. The hash is the transformation
        key. Bash and Python make it a comment. C makes a line-leading hash a
        preprocessor marker and can reject the lyric as malformed directives.
        Markdown makes line-leading hash-space lines into headings. A trailing
        inline hash remains visible instead. Meaning lives in either
        presentation and in the movement between them.
        """,
        [
            "UNRENDERED",
            "Bash / Python: # = comment",
            "C: # = preprocessor marker",
            "``` = visible fence",
            "> = visible prompt",
            "",
            "RENDERED",
            "leading # lyric = heading",
            "inline # comment = remains inline",
            "``` = terminal gathered",
            "residue = what was left out",
        ],
    ),
    _n(
        "THREE POEMS AFTER MARKDOWN",
        """
        Markdown cuts the artifact into three poems. First, the line-leading
        hash marks hidden from Bash and Python become the largest visible
        lyric. C does not hide them; it mistakes them for preprocessor
        directives and complains. Second, the fenced terminal becomes a poem
        of questioning, compiling, touching, searching, deleting, remaining,
        and absence. Third, what those two cuts leave behind contains the
        interpreter, family dynamics, the empty argument chamber, the exposed
        Godot line, identity, and the no-error return. The inline hash after
        import family does not begin a Markdown heading, so it remains visible
        in this residue and can become a stray token under C. Every parser
        misses a different whole.
        """,
        [
            "ONE — # lifts the lyric",
            "TWO — ``` gathers the terminal",
            "THREE — residue left executable",
            "",
            "# include <self>  ->  include",
            "self exists in source",
            "self vanishes in display",
        ],
    ),
    _n(
        "THE TRUE TITLE",
        """
        The true title is The, three spaces, Bed. Markdown would normally
        collapse those spaces, so they must be preserved. The filename is the
        machine that produces the title. Godot is enclosed between two
        existing spaces. Unfinished substitution keeps waiting. Failed
        substitution contributes no output. The absent value resolves to one
        Unicode space while the two surrounding spaces remain. The gap rests
        directly on the Bed.
        """,
        [
            '"The `\\(Godot)\\` Bed".py?.c.md.md',
            "",
            "(Godot) -> no output -> U+0020",
            "",
            "The + SPACE + SPACE + SPACE + Bed",
            "",
            "The   Bed",
        ],
    ),
    _n(
        "THE FILENAME SPEAKS",
        """
        The extensions read the compression aloud. Dot pee why is Python and
        pain, why. Dot C is C and see. The first dot M D is McCapes, Dylan.
        The second is Markdown and marked down. Every dot is current location:
        here. The filename says: here now, pain, why? Here still, see? Here it
        is, McCapes Dylan, expressed, marked down.
        """,
        [
            ".py?   Python / pain, why?",
            ".c     C / see",
            ".md    [m]cCapes [d]ylan",
            ".md    Markdown / marked down",
            ".      current location: here",
        ],
    ),
    _n(
        "THE CLOSED FAMILY",
        """
        The implicit tuple is family equals mother, daughter, son. It closes
        at three. Godot is parenthesized separately and cannot become member
        four. In Python, parentheses without a trailing comma are grouping,
        not even a one-member tuple. The title's parentheses are enclosure and
        sepulcher. Main void admits no arguments. Dollar four addresses the
        father-position only after the structure has closed without him.
        """,
        [
            "family = (mother, daughter, son)",
            "",
            "(Godot)          # separately enclosed",
            "main(void)       # accepts no arguments",
            "$4               # addressable, unassigned",
            "",
            '4="father" -> command not found',
        ],
    ),
    _n(
        "SHE BANG BIN — BASH",
        """
        The shebang asks the operating system to run the file through slash
        bin slash bash. Spoken, it opens: she bang bin, bash. Family is an
        extensionless file. It offers no suffix from which a desktop can infer
        a default application. This artifact supplies one route to it: the
        shell and the bin functions that access, touch, modify, and overwrite
        it. She breaks bin before the script can reach touch family. Within
        this program, no remaining operation can access or modify the file.
        Bash is interpreter and impact.
        """,
        [
            "#!/bin/bash",
            "",
            "she",
            "bang",
            "bin",
            "bash",
            "",
            "family        # extensionless file",
            "touch family  # only through the broken route",
            "",
            "broken bin -> family inaccessible",
        ],
    ),
    _n(
        "HONEST DOCUMENTATION",
        """
        A comment after a shebang normally says what a script does. Repeating
        only its filename can look lazy. Here, still yet unarrived dot C is
        exact documentation and a question: still yet unarrived, see? Dot C
        names C source and asks the reader to see. The program loads family,
        compiles children, longing and pain, waits for an absent fourth,
        preserves a process beyond disconnection, searches the whole system
        for it, survives delete as present location, and ends at an unanswered
        prompt.
        """,
        [
            "# still_yet_unarrived.c",
            "still yet unarrived. see?",
            "",
            "load family",
            "compile longing + pain",
            "seek $4",
            "persist after hangup",
            "DELETE -> . ->",
        ],
    ),
    _n(
        "FAMILY DYNAMICS / INCLUDE SELF",
        """
        Import family is executable Python runtime behavior, not a static
        declaration. When execution reaches it, Python's import machinery
        dynamically resolves and loads the module and executes its top-level
        code on the first import. Later imports normally reuse the module
        cached in sys dot modules. Its comment supplies the ordinary sentence:
        family module, dynamically loaded; family dynamics. It also spells the
        format that performs the transformation: loads M, module, D,
        dynamically; dot M D. The inline hash is the Python comment boundary
        and remains visible under Markdown. The hashes at the beginnings of
        lines become headings. The same key comments, preserves, or promotes
        according to where it stands. Family then changes from module, to
        compiler requirement, to accessed file, modified file, and output
        destination. Include self resembles C, is ignored as a shell or
        Python comment, and renders as the heading include because Markdown
        makes the self tag disappear. Self is present in source and absent in
        display.
        """,
        [
            "import family # loads module dynamically",
            "",
            "runtime -> resolve -> load -> execute",
            "later import -> sys.modules cache",
            "",
            "family module + dynamically loaded",
            "              = family dynamics",
            "loads [m]odule [d]ynamically = .md",
            "inline # remains / leading # lifts",
            "",
            "# include <self>",
            "renders as:",
            "include",
        ],
    ),
    _n(
        "PARENT PROCESS / CHILD INHERITANCE",
        """
        The shell is literally a parent process. Commands it starts are child
        processes. Set minus E declares the parent's safety boundary: stop
        after an unhandled failure instead of carrying the failed state
        forward as though nothing happened. Set minus A declares inheritance:
        variables the parent establishes are exported into child-process
        environments. The children can receive them without becoming
        arguments to main void. The source establishes E and then A: safety,
        then inheritance. The exposed line returns them as minus A E:
        inheritance and safety, with the children first, bundled into what
        must stand in for the absent father. As a standalone Bash line it is
        not a valid command invocation. As the poem's option grammar, it
        carries both parental duties back into main. Return zero says the
        speaker's absence to his children is not his error.
        """,
        [
            "parent shell",
            "",
            "set -e     # stop after unhandled failure",
            "           # safety boundary",
            "set -a     # export established state",
            "           # inheritance to child processes",
            "",
            "main(void) # no arguments",
            "-ae        # inheritance + safety",
            "",
            "return 0;  # successful completion",
            "",
            "absence != his error",
        ],
    ),
    _n(
        "UNSIGNED MAIN VOID / PRINT",
        """
        Main names the principal C body. Void says it accepts no arguments.
        Yet the compiler line requires children, longing, pain, and family.
        They are not arguments the function admits; they are conditions the
        poem requires. Uint says unsigned integer. A literal compiler may
        complain because the type needs definition, but unsigned carries its
        own weight: uncommitted, unconfirmed, without a sign. Print names
        Python output; its colon makes a C label.
        """,
        [
            "uint main(void)",
            "{",
            "    print:",
            "        [the spoken poem]",
            "}",
            "",
            "no arguments admitted",
            "children / longing / pain / family required",
        ],
    ),
    _n(
        "THE DECAY CURVE",
        """
        Ionic decay belongs to the broader ionic-potential lexicon: charge,
        the body, natural decay, and the one-over-e curve. Sharply means
        downward steepness greater than one. Steadily names slope negative
        one, forty-five degrees downward on equally scaled axes. Ever
        approaches means the steepness falls below one and tends toward zero.
        The speaker is already at the asymptotic limit, yet each day adds
        more: deepest already, still deepening.
        """,
        [
            "grief",
            "|\\",
            "| \\     sharp: |m| > 1",
            "|  \\",
            "|   \\   steady: m = -1",
            "|    \\____",
            "|         \\___ approach: |m| -> 0",
            "+------------------------------ time",
        ],
    ),
    _n(
        "GODOT MY STEAD / THE BED",
        """
        The Godot line alone leaves the indentation and hash convention. A
        close hyphen and distant em dash frame without repairing. Set E and set
        A have established safety and inheritance separately. Minus A E
        returns both with inheritance first: what the parent gives the
        children, then the boundary against carrying error forward. It is
        bundled shell-option notation, an invocation of two letters, and,
        because spoken A becomes ayee, a cry. The Juju letter already defined
        Godot as absent character and Unity as all of us together. Godot my
        stead names what occupies the father's place. The father is absent
        from family, but the two parental duties remain in the line spoken in
        his stead. The Bed is bedrock, marriage bed, death bed, and tomb:
        foundation, union and children, family goodbye, then remembrance.
        """,
        [
            "-ae Godot my stead —",
            "set -e -> safety",
            "set -a -> inheritance to children",
            "-ae    -> both duties in his stead",
            "",
            "Godot = absent character",
            "Unity = all of us Together",
            "",
            "BEDROCK -> MARRIAGE BED",
            "-> DEATH BED -> TOMB",
        ],
    ),
    _n(
        "QUESTION / COMMAND / LISTEN",
        """
        The terminal begins with a prompt receiving a question rather than an
        order. Bash answers: question mark, colon, command not found. That
        answer already supplies every token used by the next line except one:
        four. The poem adds only four, moves command into the condition, and
        rearranges Bash's error into a ternary: command four, question mark,
        not, colon, found. If command four, then not; otherwise, found. The
        unprinted alternative is listening. The operator is not submitting to
        commands. He wants people to listen. The compiler's output option is
        present. Its filename is one quoted space: a literal U plus zero zero
        two zero output that exists while appearing blank. The compiler then
        receives children, longing, pain, family, Wall, extra, and pedantic.
        Wall, extra, and pedantic are real warning flags. Warnings are not
        fatal errors.
        """,
        [
            ">?",
            "?: command not found",
            "",
            "+ four; rearrange",
            "",
            ">command four ? not : found",
            "",
            "if command four -> not",
            "else            -> found",
            "",
            ">gcc ... -o ' ' -children -longing",
            "         -pain -family -Wall -Wextra -pedantic",
            "",
            "output filename = U+0020",
        ],
    ),
    _n(
        "TWO TOUCHES",
        """
        Touch minus C minus A updates access time only if family already
        exists and stays silent if it does not. Touch minus M minus T assigns
        the recorded modification time and, because it lacks minus C, may
        create the file. After both commands, family exists, but the sequence
        can no longer prove whether it existed before. Access and modification
        are separate touches.
        """,
        [
            ">touch -c -a family",
            "  access only; do not create; silence",
            "",
            ">touch -m -t 202610090830.41 family",
            "  modification; may create",
            "",
            "afterward: family exists",
            "beforehand: no longer provable",
        ],
    ),
    _n(
        "WRITING THE EMPTY FOURTH",
        """
        Echo supplies mother, daughter, son, and trailing space. Awk numbers
        the positions. Dollar one is mother, dollar two daughter, dollar three
        son, and dollar four the operator in the father-position. No fourth
        word was supplied, so it is blank. Awk still prints the position
        through a separator, depositing Unicode space U plus zero zero two
        zero before the newline. The final redirection writes this relation to
        family.
        """,
        [
            '>echo "mother daughter son  " |',
            " awk '{print $1,$2,$3,$4}' > family",
            "",
            "$1 mother",
            "$2 daughter",
            "$3 son",
            "$4 [U+0020]",
            "",
            "mother daughter son $",
        ],
    ),
    _n(
        "THE PROCESS AT ROOT",
        """
        From the literal path home slash dylanmccapes, the first dot-dot
        reaches home and the second reaches filesystem root. Include dot-dot
        slash dot-dot slash M C C dot D therefore resolves to slash M C C dot
        D. The father omitted from the family file is placed at root, the
        foundation below home. Slash M C C dot D is beside bin. M C C dot D
        carries the literal folder name in reversed order, and it resembles a
        compiler day-mun, not a demon: the operator expressed as a system
        process. A day-mun is a
        persistent background process that waits for work and remains
        available for the next request. A compiler day-mun keeps compiler
        state, warmed workers, or cached results alive so repeated valid
        builds are faster. It cannot repair a broken script. In the poem, M C
        C dot D also reads as make compiler collection day-mun: summoned from
        the filesystem depth, persistent beside bin, waiting to be called.
        """,
        [
            "~/family",
            "",
            "~          /home/dylanmccapes",
            "..         /home",
            "../..      /  (foundation below /home)",
            "../../mcc.d -> /mcc.d",
            "",
            "/mcc.d beside /bin",
            "",
            "compiler DAY-mun",
            "persistent / cached / waiting",
            "cannot repair a broken script",
        ],
    ),
    _n(
        "PERSISTENCE / BEARING THE SOUL",
        """
        The next line begins with the blank fourth position. No-hangup asks a
        process to persist beyond disconnection. Process I D of asks for the
        numeric identity of M C C dot D. Then P S A U X bears the system's
        soul: every visible process, user, state, resource, and command. The
        pipe carries that expression into grep. Bracket M still matches M but
        prevents the search from manufacturing itself as the answer.
        """,
        [
            ">$4 nohup pidof mcc.d",
            "",
            "persist beyond disconnection",
            "seek the numeric process identity",
            "",
            ">ps aux | grep '[m]cc.d'",
            "",
            "search without manufacturing proof",
        ],
    ),
    _n(
        "DELETE → HERE → ABSENCE",
        """
        Inside the pipeline, grep ends when the process list ends. Read alone,
        grep listens until it receives an end signal or is commanded to stop.
        The poem preserves both behaviours. Caret question mark states delete,
        and zero X seven F followed by slash X two zero encodes delete plus
        space. Then the birthdays act on the bytes. M C C dot D was born July
        eleventh, nineteen ninety. His daughter F was born July twenty-first,
        twenty twenty. They share July; their days are ten apart and their
        years are thirty apart, both ending in zero. Turning those zeroes into
        letter O's and compressing the byte punctuation produces: M C C dot D,
        O X, seven F, X two O. The delete-and-space string becomes X's and O's
        between father and daughter. Dot then states the present directory:
        here, now. Dot with an open parenthesis gives Bash an unfinished
        structure. The backticks invoke the same command-substitution grammar
        carried by the title, The Godot Bed dot pee why question mark dot C
        dot M D dot M D. Bash supplies its real continuation prompt while it
        waits. The error then names the exact token in Bash's A N S I C
        notation: backtick, newline, backtick. Bash says only that the error is
        near this composite token. It does not isolate one character or
        explain the sequence's meaning. The diagnostic supplies bytes, not
        interpretation. That interpretation belongs to the operator. Cat
        minus A had already shown the father position as one space immediately
        before the dollar-sign end marker. The operator reads the dollar sign
        as Godot: the prompt and expansion sigil at the edge of an absent
        value. After it comes the newline, read as a new beginning. M C C dot D
        must enter on that new line. The error records that no command, no
        father, has entered it yet. The continuation prompt remains available
        for what can enter next. The title's parentheses, backticks, and
        unresolved chamber generate the final terminal geometry: prompt dot,
        then an empty prompt. Presence, then open waiting. These are executable
        terminal states, not decorative prompt marks. Father must enter the
        new line, and the poem ends with that line open. Delete, affection,
        here, absence. The Markdown fence closes. Command four: not.
        Listening: found.
        """,
        [
            "0x7F\\x20     DELETE + SPACE",
            "mcc.d 1990-07-11 | daughter F 2020-07-21",
            "0 -> o:  mcc.dox7Fx2o  (Xs and Os)",
            "cat -A: mother daughter son $  (Godot)",
            "NEWLINE = NEW BEGINNING",
            "father must enter the new line",
            ">^?   DELETE",
            ">.    here / presence",
            ">     open waiting",
            "\"The `\\(Godot)\\` Bed\".py?.c.md.md",
            ".( )  -> Bash continuation",
            "$'`\\n`'",
            "` + NEWLINE + `",
            "Bash: \"near\" it; meaning is the operator's",
            "DELETE -> here -> absence",
            "command four -> not",
            "listening    -> found",
        ],
    ),
]


def run(cmd: list[str], *, quiet: bool = False) -> None:
    if not quiet:
        print("+", " ".join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)


def duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        if mono
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"
        if mono
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def fit_image(path: Path, box: tuple[int, int], bg=(4, 6, 12)) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(box, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", box, bg)
    canvas.paste(image, ((box[0] - image.width) // 2, (box[1] - image.height) // 2))
    return canvas


def pair_image(left: Path, right: Path, dest: Path, label: str = "") -> None:
    canvas = Image.new("RGB", (W, H), (3, 5, 11))
    gap = 18
    margin = 24
    top = 42 if label else 18
    box_w = (W - margin * 2 - gap) // 2
    box_h = H - top - 18
    li = fit_image(left, (box_w, box_h))
    ri = fit_image(right, (box_w, box_h))
    canvas.paste(li, (margin, top))
    canvas.paste(ri, (margin + box_w + gap, top))
    if label:
        d = ImageDraw.Draw(canvas)
        d.text((margin, 10), label, font=font(22), fill=(225, 218, 195))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=94)


def draw_decay_curve(d: ImageDraw.ImageDraw) -> None:
    gold = (244, 205, 81)
    bone = (229, 224, 208)
    dim = (145, 158, 183)
    grid = (35, 45, 65)
    sharp = (238, 105, 105)
    steady = (85, 205, 151)
    approach = (105, 164, 244)

    origin_x = 116
    asymptote_y = 592
    scale = 132.0  # equal x/y scale: m = -1 is visually 45 degrees

    d.text((origin_x, 145), "IONIC POTENTIAL REMAINING", font=font(17, True), fill=dim)
    for unit in range(1, 5):
        x = origin_x + unit * scale
        d.line((x, 175, x, asymptote_y), fill=grid, width=1)
    for unit in range(1, 4):
        y = asymptote_y - unit * scale
        d.line((origin_x, y, 735, y), fill=grid, width=1)

    d.line((origin_x, 175, origin_x, asymptote_y + 16), fill=bone, width=2)
    d.line((origin_x - 7, 184, origin_x, 175, origin_x + 7, 184), fill=bone, width=2)
    d.line((origin_x, asymptote_y, 754, asymptote_y), fill=dim, width=2)
    d.line((746, asymptote_y - 7, 754, asymptote_y, 746, asymptote_y + 7), fill=dim, width=2)

    points = []
    for step in range(241):
        x = 4.55 * step / 240
        value = 3.0 * math.exp(-x)
        points.append((origin_x + x * scale, asymptote_y - value * scale))
    d.line(points, fill=gold, width=6, joint="curve")

    def tangent(x: float, color: tuple[int, int, int], span: float) -> tuple[float, float]:
        value = 3.0 * math.exp(-x)
        slope = -value
        x1, x2 = x - span, x + span
        y1 = value + slope * (x1 - x)
        y2 = value + slope * (x2 - x)
        d.line(
            (
                origin_x + x1 * scale,
                asymptote_y - y1 * scale,
                origin_x + x2 * scale,
                asymptote_y - y2 * scale,
            ),
            fill=color,
            width=4,
        )
        px, py = origin_x + x * scale, asymptote_y - value * scale
        d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=color, outline=bone, width=2)
        return px, py

    tangent(0.28, sharp, 0.24)
    tangent(math.log(3.0), steady, 0.40)
    tangent(3.05, approach, 0.66)

    d.line((origin_x, asymptote_y, 754, asymptote_y), fill=approach, width=2)
    d.text((origin_x + 12, asymptote_y + 11), "DEEPEST DEPTH / ASYMPTOTIC LIMIT", font=font(16, True), fill=approach)
    d.text((600, asymptote_y + 41), "TIME  /  EACH DAY MORE  →", font=font(16, True), fill=dim)

    box_x = 805
    rows = [
        (sharp, "SHARPLY", "|m| > 1", "steeper than 45°"),
        (steady, "STEADILY", "m = −1", "45° downward"),
        (approach, "EVER APPROACHES", "|m| → 0", "never reaches the limit"),
    ]
    for row, (color, heading, equation, note) in enumerate(rows):
        y = 185 + row * 135
        d.rounded_rectangle((box_x, y, 1224, y + 108), radius=10, outline=grid, width=2)
        d.line((box_x + 20, y + 26, box_x + 66, y + 26), fill=color, width=5)
        d.text((box_x + 80, y + 10), heading, font=font(19, True), fill=color)
        d.text((box_x + 20, y + 45), equation, font=font(25, True), fill=bone)
        d.text((box_x + 142, y + 53), note, font=font(16), fill=dim)

    d.text((805, 608), "already deepest; still deepening", font=font(18, True), fill=gold)


def slide_image(index: int, spec: dict) -> Path:
    dest = STILLS / f"tech_{index:02d}.png"
    canvas = Image.new("RGB", (W, H), (5, 7, 13))
    d = ImageDraw.Draw(canvas)
    gold = (244, 205, 81)
    bone = (229, 224, 208)
    dim = (145, 158, 183)
    d.rectangle((0, 0, W, 7), fill=gold)
    d.text((54, 38), spec["title"], font=font(34), fill=gold)
    d.text((54, 91), "THE   BED  /  TECHNICAL FIELD", font=font(16, True), fill=dim)
    d.line((54, 125, W - 54, 125), fill=(53, 66, 92), width=2)

    if spec["title"] == "THE DECAY CURVE":
        draw_decay_curve(d)
        d.text(
            (W - 210, H - 38),
            f"{index + 1:02d} / {len(NARRATION):02d}",
            font=font(15, True),
            fill=dim,
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(dest)
        return dest

    lines: list[str] = []
    for raw in spec["screen"]:
        if raw == "":
            lines.append("")
            continue
        lines.extend(textwrap.wrap(raw, width=70, replace_whitespace=False) or [""])
    f = font(24, True)
    y = 158
    for line in lines[:18]:
        color = gold if re.match(r"^(ONE|TWO|THREE|The   Bed|DELETE|command four|listening)", line) else bone
        d.text((72, y), line, font=f, fill=color)
        y += 29

    d.text(
        (W - 210, H - 38),
        f"{index + 1:02d} / {len(NARRATION):02d}",
        font=font(15, True),
        fill=dim,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)
    return dest


def load_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set ELEVENLABS_API_KEY in REALITY_USER_MANUAL/.env")
    return key


def narration_path(index: int, text: str) -> Path:
    digest = hashlib.sha256(f"Matilda|{text}|v2".encode()).hexdigest()[:16]
    return SEGMENTS / f"{index:02d}_Matilda_{digest}.mp3"


def generate_audio() -> list[dict]:
    import requests

    key = load_key()
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    cues: list[dict] = []
    t = 0.0
    for i, spec in enumerate(NARRATION):
        text = re.sub(r"\s+", " ", spec["text"]).strip()
        dest = narration_path(i, text)
        if not dest.exists() or dest.stat().st_size < 1000:
            print(f"ElevenLabs {i + 1}/{len(NARRATION)}: {spec['title']}")
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": VOICE_SETTINGS,
            }
            headers = {"xi-api-key": key, "Accept": "audio/mpeg"}
            for attempt in range(4):
                response = requests.post(
                    f"{ELEVEN}/text-to-speech/{MATILDA}",
                    headers=headers,
                    json=payload,
                    timeout=120,
                )
                if response.status_code == 200:
                    dest.write_bytes(response.content)
                    break
                if response.status_code == 429 and attempt < 3:
                    time.sleep(4 * (attempt + 1))
                    continue
                raise SystemExit(
                    f"ElevenLabs {response.status_code}: {response.text[:500]}"
                )
        dur = duration(dest)
        cues.append(
            {
                "index": i,
                "speaker": "Matilda",
                "title": spec["title"],
                "text": text,
                "file": str(dest.relative_to(BASE)),
                "start": round(t, 4),
                "end": round(t + dur, 4),
                "duration": round(dur, 4),
            }
        )
        t += dur
    AUDIO.mkdir(parents=True, exist_ok=True)
    with (AUDIO / "cues.jsonl").open("w", encoding="utf-8") as handle:
        for cue in cues:
            handle.write(json.dumps(cue, ensure_ascii=False) + "\n")
    print(f"Matilda narration: {t:.2f}s")
    return cues


def video_filter() -> str:
    return (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x03050b,"
        f"fps={FPS},format=yuv420p"
    )


def image_fragment(image: Path, seconds: float, dest: Path) -> None:
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-i", str(image), "-t", f"{seconds:.6f}",
            "-vf", video_filter(), "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", str(dest),
        ]
    )


def terminal_scroll_image(lines: list[str], label: str, dest: Path) -> None:
    line_h = 24
    top = 84
    image_h = max(H + 1, top + line_h * len(lines) + H - 110)
    canvas = Image.new("RGB", (W, image_h), (3, 7, 8))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, W, 6), fill=(0, 192, 96))
    draw.text((42, 24), label, font=font(22, True), fill=(0, 210, 110))
    body = font(17, True)
    y = top
    for raw in lines:
        line = raw.expandtabs(4)
        draw.text((42, y), line, font=body, fill=(208, 222, 211))
        y += line_h
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=94)


def scroll_fragment(image: Path, seconds: float, dest: Path) -> None:
    y_expr = f"min(max((ih-oh)*t/{seconds:.6f},0),ih-oh)"
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-i", str(image), "-t", f"{seconds:.6f}",
            "-vf", f"crop={W}:{H}:0:'{y_expr}',fps={FPS},format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", str(dest),
        ]
    )


def video_fragment(source: Path, start: float, seconds: float, dest: Path) -> None:
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(source), "-t", f"{seconds:.6f}",
            "-vf", video_filter(), "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", str(dest),
        ]
    )


def concat_video(parts: list[Path], dest: Path) -> None:
    listing = dest.with_suffix(".txt")
    listing.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8"
    )
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(listing),
            "-c", "copy", str(dest),
        ]
    )


def mux_audio(video: Path, audio: Path, dest: Path, extra: float = 0.0) -> None:
    dur = duration(audio) + extra
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(video), "-i", str(audio),
            "-filter_complex", "[1:a]aresample=48000,apad[a]",
            "-map", "0:v:0", "-map", "[a]", "-t", f"{dur:.6f}",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", str(dest),
        ]
    )


def silent_clip(video: Path, dest: Path, seconds: float | None = None) -> None:
    dur = duration(video) if seconds is None else seconds
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(video), "-f", "lavfi", "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-map", "0:v:0", "-map", "1:a:0", "-t", f"{dur:.6f}",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(dest),
        ]
    )


def still_with_audio(image: Path, audio: Path, dest: Path) -> None:
    dur = duration(audio) + 0.25
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-i", str(image), "-i", str(audio),
            "-filter_complex",
            f"[0:v]{video_filter()}[v];[1:a]aresample=48000,apad[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{dur:.6f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", str(dest),
        ]
    )


def make_opening() -> list[Path]:
    clips: list[Path] = []
    godot_launch = STAR / "solar_system_explorer/docs/demo/godot_launch.mp4"
    ant = STAR / "ant_explorer/docs/demo/ant_explorer_playthrough.mp4"
    cards = DEV / "docs/library/personal/poems/TheBed/TheBed_images"

    boot_v = WORK / "00_boot_v.mp4"
    boot_seconds = duration(godot_launch)
    video_fragment(godot_launch, 0.0, boot_seconds, boot_v)
    boot = WORK / "00_boot.mp4"
    silent_clip(boot_v, boot, boot_seconds)
    clips.append(boot)

    fronts_img = STILLS / "card_fronts.png"
    pair_image(cards / "IMG_1512.jpg", cards / "IMG_1514.jpg", fronts_img)
    fronts_v = WORK / "01_fronts_v.mp4"
    image_fragment(fronts_img, 5.0, fronts_v)
    fronts = WORK / "01_fronts.mp4"
    silent_clip(fronts_v, fronts, 5.0)
    clips.append(fronts)

    ant_v = WORK / "02_ant_v.mp4"
    video_fragment(ant, 0.0, 5.0, ant_v)
    ant_out = WORK / "02_ant.mp4"
    silent_clip(ant_v, ant_out, 5.0)
    clips.append(ant_out)
    return clips


def make_frances() -> Path:
    audio = BASE / "audio/HiFrances.m4a"
    total = duration(audio)
    sources = [
        (STAR / "solar_system_explorer/docs/demo/solar_system_explorer_playthrough.mp4", 8.0),
        (STAR / "garden_explorer/docs/demo/garden_explorer_playthrough.mp4", 24.0),
        (STAR / "math_explorer/docs/demo/math_explorer_walkthrough.mp4", 18.0),
        (STAR / "language_explorer/docs/demo/language_explorer_playthrough.mp4", 8.0),
    ]
    each = total / len(sources) + 0.05
    parts: list[Path] = []
    for i, (source, start) in enumerate(sources):
        part = WORK / f"03_frances_{i}.mp4"
        video_fragment(source, start, each, part)
        parts.append(part)
    visual = WORK / "03_frances_visual.mp4"
    concat_video(parts, visual)
    out = WORK / "03_frances.mp4"
    mux_audio(visual, audio, out)
    return out


def make_juju() -> Path:
    audio = BASE / "audio/HiJuju.m4a"
    total = duration(audio)
    kangaroo = STAR / "kangaroo_park"
    stills = [
        kangaroo / "matilda_reconstruction/renders/anatomy_bones.png",
        kangaroo / "matilda_reconstruction/renders/anatomy_polygons.png",
    ]
    movies = [
        kangaroo / "matilda_reconstruction/renders/matilda_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/australotitan/renders/cooper_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/muttaburrasaurus/renders/muttaburrasaurus_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/kronosaurus/renders/kronosaurus_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/ankylosaurus/renders/ankylosaurus_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/stegosaurus/renders/stegosaurus_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/leaellynasaura/renders/leaellynasaura_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/australovenator/renders/australovenator_four_behaviors.mp4",
        kangaroo / "animal_reconstructions/procoptodon/renders/procoptodon_four_behaviors.mp4",
    ]
    still_dur = 1.5
    movie_dur = (total - still_dur * len(stills)) / len(movies) + 0.03
    parts: list[Path] = []
    for i, source in enumerate(stills):
        part = WORK / f"04_juju_still_{i}.mp4"
        image_fragment(source, still_dur, part)
        parts.append(part)
    for i, source in enumerate(movies):
        part = WORK / f"04_juju_animal_{i}.mp4"
        video_fragment(source, 0.0, movie_dur, part)
        parts.append(part)
    visual = WORK / "04_juju_visual.mp4"
    concat_video(parts, visual)
    out = WORK / "04_juju.mp4"
    mux_audio(visual, audio, out)
    return out


def make_bed() -> Path:
    video = STAR / "solar_system_explorer/docs/demo/zecliptic_angle_flight.mp4"
    audio = BASE / "audio/TheBed.m4a"
    source = WORK / "05_bed_visual.mp4"
    video_fragment(video, 0.0, duration(audio) + 0.03, source)
    out = WORK / "05_bed.mp4"
    mux_audio(source, audio, out)
    return out


def make_technical() -> list[Path]:
    clips: list[Path] = []
    for i, spec in enumerate(NARRATION):
        slide = slide_image(i, spec)
        text = re.sub(r"\s+", " ", spec["text"]).strip()
        audio = narration_path(i, text)
        if not audio.exists():
            raise SystemExit(f"missing narration: {audio}; run audio first")
        clip = WORK / f"tech_{i:02d}.mp4"
        still_with_audio(slide, audio, clip)
        clips.append(clip)
    return clips


def make_ending() -> Path:
    cards = DEV / "docs/library/personal/poems/TheBed/TheBed_images"
    image = STILLS / "card_insides_final.png"
    pair_image(cards / "IMG_1511.jpg", cards / "IMG_1513.jpg", image)
    visual = WORK / "99_open_cards_v.mp4"
    image_fragment(image, 15.0, visual)
    out = WORK / "99_open_cards.mp4"
    silent_clip(visual, out, 15.0)
    return out


def make_epilogue() -> list[Path]:
    root = DEV / "docs/library/personal/poems/TheBed"
    audio = BASE / "audio/SoonUnity.m4a"
    walkthrough = (root / "TerminalWalkthrough").read_text(encoding="utf-8").splitlines()
    ranges = [
        (walkthrough[21:84], "TERMINAL WALKTHROUGH  /  LINES 22–84"),
        (walkthrough[124:187], "TERMINAL WALKTHROUGH  /  LINES 125–187"),
    ]
    total_lines = sum(len(lines) for lines, _ in ranges)
    audio_dur = duration(audio)
    scroll_parts: list[Path] = []
    for i, (lines, label) in enumerate(ranges):
        seconds = audio_dur * len(lines) / total_lines
        plate = STILLS / f"epilogue_scroll_{i}.png"
        terminal_scroll_image(lines, label, plate)
        part = WORK / f"100_epilogue_scroll_{i}.mp4"
        scroll_fragment(plate, seconds, part)
        scroll_parts.append(part)
    scroll_visual = WORK / "100_epilogue_scroll_visual.mp4"
    concat_video(scroll_parts, scroll_visual)
    history = WORK / "100_epilogue_history.mp4"
    mux_audio(scroll_visual, audio, history)

    images = root / "TheBed_images" / "epilogue"
    order = [
        "IMG_0250.jpg",
        "IMG_1063.jpg",
        "IMG_0225.jpg",
        "IMG_0488.jpg",
        "IMG_0002.jpg",
        "Jacqueline Wall_Natasha Fontarensky_Old Mill Park_SF Bay_2020-12-19 1130am_1608526952_recnFSP96v5V6yzf0_139_137.jpg",
        "Jacqueline Wall_Natasha Fontarensky_Old Mill Park_SF Bay_2020-12-19 1130am_1608526952_recnFSP96v5V6yzf0_143_141.jpg",
        "Jacqueline Wall_Natasha Fontarensky_Old Mill Park_SF Bay_2020-12-19 1130am_1608526952_recnFSP96v5V6yzf0_144_142.jpg",
        "IMG_3821.jpg",
        "IMG_0121.jpg",
        "IMG_0152.jpg",
        "IMG_0204.jpg",
        "IMG_0328.jpg",
        "IMG_0998.jpg",
        "IMG_1142.jpg",
        "66856538380__E1F8CA2C-F73E-439D-A967-7D6C2FF51100.jpg",
        "IMG_0808.jpg",
        "IMG_3588.jpg",
        "IMG_3832.jpg",
        "IMG_2205.jpg",
        "IMG_5941.jpg",
        "FullSizeRender.jpg",
        "IMG_2882.jpg",
        "IMG_5032.jpg",
        "IMG_5038.jpg",
        "IMG_5065.jpg",
        "IMG_5076.jpg",
    ]
    still_seconds = 2.4
    still_parts: list[Path] = []
    for i, name in enumerate(order):
        source = images / name
        if not source.exists():
            raise SystemExit(f"missing epilogue image: {source}")
        part = WORK / f"101_epilogue_image_{i:02d}.mp4"
        image_fragment(source, still_seconds, part)
        still_parts.append(part)
    slideshow_visual = WORK / "101_epilogue_slideshow_visual.mp4"
    concat_video(still_parts, slideshow_visual)
    slideshow = WORK / "101_epilogue_slideshow.mp4"
    silent_clip(slideshow_visual, slideshow, still_seconds * len(order))
    return [history, slideshow]


def assemble() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    STILLS.mkdir(parents=True, exist_ok=True)

    required = [
        BASE / "audio/HiFrances.m4a",
        BASE / "audio/HiJuju.m4a",
        BASE / "audio/TheBed.m4a",
        BASE / "audio/SoonUnity.m4a",
        DEV / "docs/library/personal/poems/TheBed/TerminalWalkthrough",
        STAR / "solar_system_explorer/docs/demo/godot_launch.mp4",
        STAR / "solar_system_explorer/docs/demo/zecliptic_angle_flight.mp4",
    ]
    for path in required:
        if not path.exists():
            raise SystemExit(f"missing required source: {path}")

    clips = make_opening()
    clips += [make_frances(), make_juju(), make_bed()]
    clips += make_technical()
    clips += [make_ending()]
    clips += make_epilogue()

    listing = WORK / "final_concat.txt"
    listing.write_text(
        "".join(f"file '{clip.resolve()}'\n" for clip in clips),
        encoding="utf-8",
    )
    run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(listing),
            "-c", "copy", "-movflags", "+faststart", str(FINAL),
        ]
    )
    manifest = {
        "output": str(FINAL.relative_to(BASE)),
        "duration": duration(FINAL),
        "width": W,
        "height": H,
        "fps": FPS,
        "matilda_segments": len(NARRATION),
        "clips": [str(p.relative_to(BASE)) for p in clips],
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["audio", "assemble", "all"])
    args = parser.parse_args()
    if args.command in {"audio", "all"}:
        generate_audio()
    if args.command in {"assemble", "all"}:
        assemble()


if __name__ == "__main__":
    main()

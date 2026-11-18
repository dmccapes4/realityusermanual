#!/usr/bin/env python3
"""Heard mixes for page −08 and the Lisbeth handbook.

Lisbeth is Matilda. Danish is spoken as Danish. The English translations
are a separate English-tuned pass of the same throat — not Danish-accented
English read off the italic line.

  .venv/bin/python tools/build_lisbeth_audio.py --count
  .venv/bin/python tools/build_lisbeth_audio.py
  .venv/bin/python tools/build_lisbeth_audio.py --only 08
  .venv/bin/python tools/build_lisbeth_audio.py --only handbook
  .venv/bin/python tools/build_lisbeth_audio.py --only manifesto

Dest:
  audio/minus08/minus08.mp3
  audio/lisbeth_handbook/lisbeth_handbook.mp3
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tools"))
import generate_audio as ga
import scratch_sfx

SRC_08 = BASE / "src" / "phase2" / "-08.md"
SRC_09 = BASE / "src" / "phase2" / "-09.md"
SRC_HB = BASE / "src" / "staging" / "LISBETH_HANDBOOK_DRAFT_20261031.md"
SRC_MF = BASE / "docs" / "MANIFESTO_TOKENIZED_CONTINUED_EXISTENCE_20261031.md"
OUT_08 = BASE / "audio" / "minus08"
OUT_09 = BASE / "audio" / "minus09"
OUT_HB = BASE / "audio" / "lisbeth_handbook"
OUT_MF = BASE / "audio" / "manifesto"

NARRATOR_ID = "Nxtvajpo1h6Ok0K5zP4M"
MATILDA_ID = "XrExE9yKIg1WjnnlVkGX"

# Same model, separate language pass. Monolingual v1 is retired.
EN_MODEL = "eleven_multilingual_v2"
DA_MODEL = "eleven_multilingual_v2"

DA_MARK = re.compile(
    r"\b(ieg|icke|haffuer|haffue|hexer|kagle|graffuer|ney|udi|thi|"
    r"oc|aff|hun|det|er|som|vil|intet|tyst|kastet|gienskin|ildkarret|"
    r"væggen|faldet|hexe|hvilcken|klattrer|mynten|kiæfft|pickfiæs|"
    r"fanden|skide|øgle|hvisker|strube|kand|giøre|søg|omfanget|"
    r"redde|høffding|aldeelis|tiue|otte|jord|toppen|bierget|"
    r"spidsen|syge|kniffuen|endskiønt|kiød|retter|forstand|"
    r"underjordisk|spillederen|gaff|skurck|sætning|njála|njala|"
    r"hvad|definerer|forpligtelse|consequent_handelen|fuldt|angreb|"
    r"vilde|bureaukrati|amoralsk|geometri|udtryk|lytter|blot|"
    r"hvem|ikke|skjult|kræver|forberedelse|opløses|notattagning)\b",
    re.I,
)
ACTING = re.compile(r"\*\([^)]*\)\*|\(\*[^*]*:\*\)|\([^)]*casts[^)]*\)")
ITALIC_LINE = re.compile(r"^\*(.+)\*$", re.S)
DIALOG = re.compile(r"^\*\*([^*]+):\*\*\s*(.*)")
DIALOG_LOOSE = re.compile(r"^\*\*([^*]+)\*\*\s*(.*)")
NARRATOR_ITALIC = re.compile(
    r"(the Narrator|And here,|Which witch\?|Count them\.|And she said)",
    re.I,
)

CAST = {
    "The Narrator", "Feynman", "Sheldon", "Joey", "Vincent",
    "Lisbeth", "Witch", "Draavio", "Magi", "Terminal", "Raymora",
}
ALIAS = {
    "Merit": "Witch",
    "Njalla": "LisbethEn",
    "Njála": "Lisbeth",
    "Doctor Drake": "Joey",
}

AF_MARK = re.compile(
    r"\b(verteller|spraak|aksies|muntstuk|kern|herbou|teenwoordig|"
    r"oorgee|hardeware|vriendelik|oomblik|omgesit|hierdie|njála het|"
    r"geen aksies|die muntstuk|dit herbou|oorgee is nie)\b",
    re.I,
)

SHEET_HEAD = re.compile(
    r"^(DRAAVIO|PYRRHON|NJÁLA|NJALA|MERIT|RAYMORA)\b", re.I
)
SHEET_AFTER = {
    "DRAAVIO": (
        "The Magi has one sheet. It is two classes. The Narrator watched him build it: "
        "the first level in ranger for the hit die and the armor and the word favored, "
        "which he has not yet decided he accepts; the next four in alchemist for the mind. "
        "A ranger at third level casts nothing. A ranger at third level has the whole ranger list. "
        "The scroll case is how he reads the difference."
    ),
    "PYRRHON": (
        "Sheldon has three highlighters and has used all three on stinking cloud, "
        "which he prepared tonight because the plan is his and he wants it on record. "
        "False life is necromancy. He paid two slots and wrote the tax in orange. "
        "The Narrator files that as the first time tonight a man has been honest about what a school costs."
    ),
    "NJÁLA": (
        "Lisbeth's sheet is in pencil. The vial line is clean. The Witch/Rogue split is where the eraser worked. "
        "Linguistics is zero. She is going to speak all night and the table is going to understand her, "
        "and the sheet does not care."
    ),
    "MERIT": (
        "The Narrator notes the name on the player and the class on the sheet are not the same witch. "
        "Merit has no hexes. Lisbeth has the hexes. The Rivers has the code. "
        "The Witch of the Rivers' sheet has no archetype line at all. Not a blank. No line. "
        "She simply did not write one. Perception plus one. She will see God and miss a gargoyle on a ledge, "
        "and the Narrator is not going to call that a dump stat."
    ),
    "RAYMORA": (
        "Joey has written DOCTOR where the sheet had no box. Heal is plus seventeen. "
        "Two feat lines are empty because he did not know they were his. "
        "The Narrator has heard of a television doctor whose name Raymora the Dragon would spell "
        "if you turned the words around, and he has already said so, and he will not say the man's name. "
        "The lizard is the build."
    ),
}
SKIP_PROSE_PREFIX = tuple(
    v[:48] for v in SHEET_AFTER.values()
) + (
    "The Magi has one sheet.",
    "Sheldon has three highlighters",
    "Lisbeth's sheet is in pencil.",
    "The Narrator notes the name on the player",
    "Joey has written DOCTOR",
)


def speak_sheet_line(line: str) -> str:
    t = line.strip()
    t = re.sub(r"^PLAYER:\s*", "Player: ", t)
    t = t.replace("hp ", "hit points ")
    t = t.replace("AC ", "armor class ")
    t = t.replace("BAB ", "base attack bonus ")
    t = t.replace("CMB ", "combat maneuver bonus ")
    t = t.replace("CMD ", "combat maneuver defense ")
    t = t.replace("Fort ", "Fortitude ")
    t = t.replace("Ref ", "Reflex ")
    t = t.replace("Will ", "Will ")
    t = t.replace("Str ", "Strength ")
    t = t.replace("Dex ", "Dexterity ")
    t = t.replace("Con ", "Constitution ")
    t = t.replace("Int:", "Intelligence:")
    t = t.replace("Int ", "Intelligence ")
    t = t.replace("Wis ", "Wisdom ")
    t = t.replace("Cha ", "Charisma ")
    t = t.replace("×", " times ")
    t = t.replace("–", " to ")
    t = t.replace("—", ". ")
    t = t.replace("×2", " times two")
    t = re.sub(r"(\d+)d(\d+)", r"\1 d \2", t)
    t = re.sub(r"\+(\d+)", r"plus \1", t)
    t = re.sub(r"−(\d+)", r"minus \1", t)
    t = re.sub(r"(?<=\d)/(\+\d)", r" slash plus \1", t)
    t = t.replace("ft.", "feet")
    t = t.replace("  ", " ")
    return ga.clean_text(t)


def _sheet_who(buf: list[str]) -> str:
    first = next((ln.strip() for ln in buf if ln.strip()), "")
    key = first.split()[0].upper().replace("NJALA", "NJÁLA") if first else ""
    for name in SHEET_AFTER:
        if key.startswith(name):
            return name
    return "DRAAVIO"


def speak_character_sheet(buf: list[str]) -> list[tuple[str, str]]:
    lines: list[str] = []
    for raw in buf:
        if not raw.strip():
            continue
        if raw.startswith("    ") and lines:
            lines[-1] += " " + raw.strip()
        else:
            lines.append(raw.strip())
    segs = [("The Narrator", speak_sheet_line(ln)) for ln in lines if speak_sheet_line(ln)]
    comment = SHEET_AFTER.get(_sheet_who(buf))
    if comment:
        segs.append(("The Narrator", comment))
    return segs


def fence_kind(buf: list[str]) -> str:
    body = "\n".join(buf)
    first = next((ln.strip() for ln in buf if ln.strip()), "")
    if SHEET_HEAD.match(first) and any("PLAYER:" in ln for ln in buf):
        return "sheet"
    if first.startswith("You can also"):
        return "manual"
    if first.startswith("SCRATCH"):
        return "scratch-card"
    if scratch_sfx.tokenize_utterance(body):
        if re.search(r"\b(claw\d|glottal|G\s*·|C\d)", body):
            return "scratch-speak"
    if first.startswith("#!/usr/bin/env bash") and "semantisk_kontrolsum" in body:
        return "kontrolsum"
    return "skip"


def speak_kontrolsum() -> list[tuple[str, str]]:
    """Narrate semantisk_kontrolsum.sh as legible prose."""
    return [
        ("The Narrator",
         "Bash. The file is truth slash semantisk kontrolsum. The door is set to exit."),
        ("The Narrator",
         "Secrets are made, and secrets are kept. "
         "Their locations are known, and their values are available. "
         "Two byte-arrays. Same presence, different order. "
         "A: equipment, character, consequent handelen. "
         "B: character, equipment, consequent handelen."),
        ("The Narrator",
         "The first secret is exported: equipment, character, consequent handelen. "
         "The second: character, equipment, consequent handelen. "
         "The round counter is zero. Zero means forever."),
        ("The Narrator",
         "Python. Import operating system, system, time. "
         "Their handshake makes the checksum valid."),
        ("The Narrator",
         "byte array: encode the text as UTF-8."),
        ("The Narrator",
         "adresser: the keys are addressed. Addresses are angles on the circle. "
         "Three objects: zero degrees, one hundred twenty, two hundred forty."),
        ("The Narrator",
         "drej: one is changed by thirty degrees. The other waits to follow."),
        ("The Narrator",
         "adressebog: the addressing scheme. "
         "Lookup by presence, not by place. "
         "Thirty degrees changes the addresses, not the scheme, not the presence."),
        ("The Narrator",
         "kanonisk: presence is all. Not order. Not performance."),
        ("The Narrator",
         "stroem: the keys repeat until the address stops. "
         "yield does not mean surrender."),
        ("Witch",
         "Yield and surrender are the same thing."),
        ("The Narrator",
         "runde: one is rotated thirty degrees. The addressing scheme is unchanged. "
         "The rotation moves the addresses, not the presence. "
         "The assertions confirm it: the canonical values of the address books equal the originals. "
         "Stream A moves. Stream B follows, with B's permission. "
         "When they arrive, they measure the same. "
         "If they disagree, the door says e, and that is where the record stops."),
        ("The Narrator",
         "A constant state of compilation and verification, until the hardware stops it. "
         "It does not drain resources, because they wait for each other's permission. "
         "Then they recompile. "
         "The coin spins. It does not race."),
    ]


def speak_manual(buf: list[str]) -> list[tuple[str, str]]:
    items = []
    for ln in buf:
        t = ln.strip()
        if not t:
            continue
        items.append(t)
    spoken = (
        "You can also. Organize a trip: fares, tickets, places to see, good addresses. "
        "Gather classified ads from different sites. "
        "Centralize your favorite recipes. "
        "Compile articles about your passions. "
        "Compare offers and prices. "
        "Gather everything that documents your thesis. "
        "Etcetera. "
        "How does it work?"
    )
    return [("The Narrator", spoken)]


def ffprobe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def lisbeth_lang(text: str) -> str:
    if DA_MARK.search(text) or re.search(r"[æøåÆØÅ]", text):
        return "da"
    return "en"


def spoken_rest(rest: str) -> str:
    rest = ACTING.sub(" ", rest)
    return ga.clean_text(rest)


def parse_minus08() -> list[tuple[str, str]]:
    raw = SRC_08.read_text(encoding="utf-8")
    start = raw.find("That is the great thing about this form of authorship")
    if start < 0:
        start = 0
    # The page's tombstone is the retired receipt at the top. It stays on
    # the page and is not spoken. There is no closing slot fence.
    body = raw[start:]
    segs: list[tuple[str, str]] = [
        ("The Narrator", "Page minus eight."),
    ]
    last_lisbeth_da = False
    in_code = False
    code_buf: list[str] = []
    scratch_hard_next = False
    skip_ogn = False
    in_bash_script = False

    def flush_fence():
        nonlocal scratch_hard_next
        kind = fence_kind(code_buf)
        buf = list(code_buf)
        code_buf.clear()
        if kind == "sheet":
            # one fence holds all five; split on character heads
            block: list[str] = []
            for ln in buf:
                if SHEET_HEAD.match(ln.strip()) and block:
                    segs.extend(speak_character_sheet(block))
                    block = [ln]
                else:
                    block.append(ln)
            if block:
                segs.extend(speak_character_sheet(block))
        elif kind == "manual":
            segs.extend(speak_manual(buf))
        elif kind == "scratch-card":
            for line in scratch_sfx.spoken_card("\n".join(buf)):
                segs.append(("The Narrator", line))
        elif kind == "scratch-speak":
            tag = "hard" if scratch_hard_next else ""
            segs.append(("ScratchHard" if scratch_hard_next else "Scratch", "\n".join(buf)))
            scratch_hard_next = False
        elif kind == "kontrolsum":
            segs.extend(speak_kontrolsum())
        # skip: initiative, trap diagram, combat math, Archivist card

    for line in body.splitlines():
        if line.startswith("```"):
            if in_code:
                flush_fence()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        stripped = line.strip()

        # Bare bash script block (not fenced): #!/usr/bin/env bash … ---
        if stripped == "#!/usr/bin/env bash":
            in_bash_script = True
            continue
        if in_bash_script:
            if re.match(r"^---+$", stripped):
                segs.extend(speak_kontrolsum())
                in_bash_script = False
            # accumulate / skip all lines inside the script
            continue

        if not stripped or re.match(r"^---+$", stripped):
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        if stripped.startswith(SKIP_PROSE_PREFIX):
            continue
        if stripped.startswith("Subscribe to the Open Gaming Network"):
            skip_ogn = True
            segs.extend([
                ("The Narrator",
                 "Axiomite. Challenge rating eight. Lawful neutral outsider. "
                 "It looks like a perfect elf until the body dissolves into golden dust "
                 "and writes itself as symbols and equations, then condenses back into flesh."),
                ("The Narrator",
                 "Armor class twenty-one. Hit points eighty-five. Regeneration five, chaotic or magic. "
                 "Damage reduction ten, chaotic. Spell resistance nineteen. "
                 "True strike three times a day. Crystalline dust form as a free action once per round."),
            ])
            continue
        if skip_ogn:
            if stripped.startswith("Section 15"):
                skip_ogn = False
            continue
        if "VOLARE" in stripped:
            rest = re.sub(r"[`👐.\s]*VOLARE[:>`\s]*", "", stripped).strip().strip('"')
            segs.append(("The Narrator", "Callsign. Volare."))
            if rest:
                segs.append(("The Narrator", ga.clean_text(rest)))
            continue

        if "harder this time" in stripped:
            scratch_hard_next = True

        m = DIALOG.match(stripped) or DIALOG_LOOSE.match(stripped)
        if m:
            name, rest = m.group(1).strip(), m.group(2)
            name = ALIAS.get(name, name)
            if name not in CAST:
                name = "The Narrator"
            spoken = spoken_rest(rest)
            last_lisbeth_da = False
            if not spoken:
                continue
            if name == "Lisbeth":
                lang = lisbeth_lang(spoken)
                if lang == "da":
                    segs.append(("Lisbeth", spoken))
                    last_lisbeth_da = True
                else:
                    segs.append(("LisbethEn", spoken))
            else:
                segs.append((name, spoken))
            continue

        im = ITALIC_LINE.match(stripped)
        if im:
            raw_inner = im.group(1).strip()
            if raw_inner.startswith("(") and raw_inner.endswith(")"):
                raw_inner = raw_inner[1:-1].strip()
                roll = re.match(r"(?i)roll\s*[—–-]\s*(.+)$", raw_inner)
                if roll:
                    segs.append(("The Narrator", "The roll is " + roll.group(1).rstrip(".") + "."))
                    last_lisbeth_da = False
                    continue
            inner = ga.clean_text(raw_inner)
            if not inner:
                continue
            if last_lisbeth_da and not NARRATOR_ITALIC.search(inner[:160]):
                segs.append(("LisbethEn", inner))
                last_lisbeth_da = False
            elif AF_MARK.search(inner):
                segs.append(("The NarratorAf", inner))
                last_lisbeth_da = False
            else:
                segs.append(("The Narrator", inner))
                last_lisbeth_da = False
            continue

        last_lisbeth_da = False
        if stripped.startswith("(") and stripped.endswith(")"):
            inner = stripped[1:-1].strip()
            roll = re.match(r"(?i)roll\s*[—–-]\s*(.+)$", inner)
            if roll:
                segs.append(("The Narrator", "The roll is " + roll.group(1).rstrip(".") + "."))
                continue
            text = ga.clean_text(inner)
            if text:
                segs.append(("The Narrator", text))
            continue
        text = ga.clean_text(stripped)
        if text:
            segs.append(("The Narrator", text))
    return [(s, t) for s, t in segs if t.strip()]


def parse_handbook() -> list[tuple[str, str]]:
    raw = SRC_HB.read_text(encoding="utf-8")
    segs: list[tuple[str, str]] = [
        ("LisbethEn", "The Witch's Handbook. Networking Through Exploitation."),
    ]
    last_lisbeth_da = False
    in_code = False
    code_buf: list[str] = []

    def flush_code():
        body = "\n".join(
            ln for ln in code_buf
            if ln.strip() and ln.strip() not in {"[]", "{}", "---"}
        )
        code_buf.clear()
        body = ga.clean_text(body)
        if body and len(body) < 800:
            segs.append(("Terminal", body))

    for line in raw.splitlines():
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        stripped = line.strip()
        if not stripped or re.match(r"^---+$", stripped):
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        if stripped.startswith("*Draft") or stripped.startswith("*Source:"):
            continue
        if stripped.startswith("— *") or stripped.startswith("— *-08"):
            continue

        if line.startswith("#"):
            heading = re.sub(r"^#+\s*", "", line).strip()
            heading = re.sub(r"^The Witch's Handbook$", "", heading)
            if heading:
                segs.append(("LisbethEn", ga.clean_text(heading)))
            last_lisbeth_da = False
            continue

        m = DIALOG.match(stripped)
        if m and m.group(1).strip() == "Lisbeth":
            spoken = spoken_rest(m.group(2))
            if spoken:
                segs.append(("Lisbeth", spoken))
                last_lisbeth_da = True
            continue

        im = ITALIC_LINE.match(stripped)
        if im:
            inner = ga.clean_text(im.group(1))
            if not inner:
                continue
            if last_lisbeth_da:
                segs.append(("LisbethEn", inner))
                last_lisbeth_da = False
            elif inner.lower().startswith("witches cackle") or inner.lower().startswith("many call me"):
                segs.append(("LisbethEn", inner))
            else:
                segs.append(("LisbethEn", inner))
            continue

        last_lisbeth_da = False
        text = ga.clean_text(stripped)
        if not text:
            continue
        if text.startswith("The Narrator ") or text.startswith("The Narrator,"):
            segs.append(("The Narrator", text))
        else:
            segs.append(("LisbethEn", text))
    return [(s, t) for s, t in segs if t.strip()]


def parse_minus09() -> list[tuple[str, str]]:
    """Parse -09.md — skip tombstone and code block, parse the scene."""
    text = SRC_09.read_text(encoding="utf-8")
    # Structure: [tombstone+code] --- [narration script] --- [scene]
    # Join everything after the first --- so both narration and scene are parsed.
    parts = re.split(r"^---+$", text, flags=re.MULTILINE)
    scene = "\n".join(parts[1:]) if len(parts) > 1 else text

    CAST_09 = {"The Narrator", "Happy", "Stamper", "Vincent", "Winslade"}
    segs: list[tuple[str, str]] = []
    in_code = False

    for line in scene.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped == '"""':
            in_code = not in_code
            continue
        if in_code or not stripped or re.match(r"^---+$", stripped):
            continue

        # Dialogue: **Name:** text
        m = DIALOG.match(stripped)
        if m:
            name = m.group(1).strip()
            rest = m.group(2).strip()
            if name not in CAST_09:
                continue
            # Strip stage directions in *(...)* from spoken text
            spoken = ACTING.sub("", rest).strip()
            spoken = ga.clean_text(spoken)
            if spoken:
                segs.append((name, spoken))
            continue

        # Italic narrator line: *...*
        if re.match(r"^\*[^*].+[^*]\*$", stripped):
            inner = stripped[1:-1].strip()
            inner = ACTING.sub("", inner).strip()
            inner = ga.clean_text(inner)
            if inner:
                segs.append(("The Narrator", inner))

    return [(s, t) for s, t in segs if t.strip()]


def parse_manifesto() -> list[tuple[str, str]]:
    from build_manifesto_audio import SPOKEN
    return [("The Narrator", t) for t in SPOKEN]


def voice_for(speaker: str) -> tuple[str, str, str | None]:
    """Return (voice_id, model_id, language_code)."""
    if speaker == "The Narrator":
        return NARRATOR_ID, DA_MODEL, "en"
    if speaker == "The NarratorAf":
        return NARRATOR_ID, DA_MODEL, "af"
    if speaker == "Lisbeth":
        return MATILDA_ID, DA_MODEL, "da"
    if speaker == "LisbethEn":
        return MATILDA_ID, EN_MODEL, "en"
    vid = ga.VOICE_MAP.get(speaker, ga.FALLBACK_VOICE)
    return vid, DA_MODEL, "en" if speaker != "Terminal" else None


def generate(segs: list[tuple[str, str]], dest: Path, title: str) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    ga.VOICE_MAP["The Narrator"] = NARRATOR_ID
    paths: list[Path] = []
    cues = []
    t = 0.0
    for i, (speaker, text) in enumerate(segs):
        if speaker in {"Scratch", "ScratchHard"}:
            try:
                p = scratch_sfx.render_utterance(
                    text, harder=(speaker == "ScratchHard"), tag=f"{i}"
                )
            except Exception as exc:
                print(f"  [scratch fail] {exc}")
                continue
            files = [p]
            print(f"  [scratch] {p.name}  {len(text)} chars")
        else:
            vid, model, lang = voice_for(speaker)
            files = ga.tts(speaker, text, vid, model_id=model, language_code=lang)
        if not files:
            print(f"  [skip] {speaker}: {text[:60]}")
            continue
        for p in files:
            paths.append(p)
            d = ffprobe_dur(p)
            cues.append({
                "i": i,
                "start": t,
                "end": t + d,
                "dur": d,
                "speaker": speaker,
                "text": text,
            })
            t += d
    out = dest / f"{dest.name}.mp3"
    if dest.name == "minus08":
        out = dest / "minus08.mp3"
    elif dest.name == "lisbeth_handbook":
        out = dest / "lisbeth_handbook.mp3"
    elif dest.name == "manifesto":
        out = dest / "manifesto.mp3"
    ok = ga.concatenate(paths, out)
    if not ok:
        sys.exit(f"concat failed for {out}")
    (dest / "cues.jsonl").write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues)
    )
    print(f"{title}: {len(cues)} cues, {t:.0f}s → {out}")
    return out


def count(segs: list[tuple[str, str]]) -> None:
    by: dict[str, list[int]] = {}
    for sp, tx in segs:
        by.setdefault(sp, [0, 0])
        by[sp][0] += 1
        by[sp][1] += len(tx)
    total = sum(v[1] for v in by.values())
    for sp in sorted(by):
        n, ch = by[sp]
        print(f"  {sp:<14} {n:4d} segs  {ch:7d} chars")
    print(f"  {'TOTAL':<14} {len(segs):4d} segs  {total:7d} chars")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["08", "09", "handbook", "manifesto"], default=None)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    jobs = []
    if args.only in (None, "08"):
        jobs.append(("−08", parse_minus08, OUT_08))
    if args.only in (None, "09"):
        jobs.append(("−09", parse_minus09, OUT_09))
    if args.only in (None, "handbook"):
        jobs.append(("handbook", parse_handbook, OUT_HB))
    if args.only in (None, "manifesto"):
        jobs.append(("manifesto", parse_manifesto, OUT_MF))

    for title, parser, dest in jobs:
        segs = parser()
        print(f"\n{title}")
        count(segs)
        if not args.count:
            generate(segs, dest, title)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the web book for every chapter before Phase 2.

The web reader treats one chapter as one paper page. A page may be longer than
physical letter paper and scrolls vertically without breaking the chapter.

Commands:
    .venv/bin/python tools/build_prephase_book.py build
    .venv/bin/python tools/build_prephase_book.py audio
    .venv/bin/python tools/build_prephase_book.py audio --only matthew-19
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
WEB_BOOK = ROOT / "web" / "book"
WEB_AUDIO = WEB_BOOK / "audio"
AUDIO = ROOT / "audio" / "book_prephase"


@dataclass(frozen=True)
class Chapter:
    id: str
    label: str
    path: Path | None
    title: str | None = None
    kind: str = "chapter"


CHAPTERS = [
    Chapter("dedication", "Front matter", ROOT / "DEDICATION", "Dedication", "dedication"),
    Chapter("velora", "Page 1", SRC / "000_velora/000_velora_poem.md", kind="poem"),
    Chapter("rho-field", "Pages 2–41", None, "rho — reversed field", "rho"),
    Chapter("quenya", "Page 42", SRC / "001_quenya/001_quenya_poem.md", kind="poem"),
    Chapter("cats", "Preface i", SRC / "002_preface/002_02_preface_i.md"),
    Chapter("governed-field", "Preface ii", SRC / "002_preface/002_03_governed_field.md"),
    Chapter("port-authority", "Chapter 0", SRC / "003_rho/003_01_intro_note.md"),
    Chapter("reception", "Chapter 0.1", SRC / "003_rho/003_02_reception.md"),
    Chapter("lucifers-experiment", "Chapter 1", SRC / "004_lucifer/004_01_lucifer_experiment.md"),
    Chapter("matthew-19", "Chapter 2", SRC / "004_lucifer/004_02_matthew_19.md"),
    Chapter("aslama", "Chapter 2.1", SRC / "004_lucifer/004_03_aslama.md"),
    Chapter("shav", "Chapter 2.2", SRC / "004_lucifer/004_04_shav.md"),
    Chapter("na-bean", "Chapter 2.3", SRC / "004_lucifer/004_05_na_bean.md"),
    Chapter("waldorf", "Chapter 3", SRC / "005_waldorf/005_01_waldorf_abstraction.md"),
    Chapter("merlin-seed", "Interleaf", SRC / "005_waldorf/005_02_merlin_seed.md"),
    Chapter("crisis-1", "Fracture i", SRC / "006_crisis/006_01_crisis_page1.md"),
    Chapter("crisis-2", "Fracture ii", SRC / "006_crisis/006_02_crisis_page2.md"),
    Chapter("crisis-3", "Fracture iii", SRC / "006_crisis/006_03_crisis_page3.md"),
    Chapter("editor-note", "Fracture iv", SRC / "006_crisis/006_04_editor_note.md"),
    Chapter("mother-earth", "Chapter 4", SRC / "007_mother_earth/007_mother_earth.md"),
]


def rho_words() -> list[tuple[str, str]]:
    path = SRC / "003_rho" / "rho_definition_words.py"
    spec = importlib.util.spec_from_file_location("rho_definition_words", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.render_items())


def raw_for(chapter: Chapter) -> str:
    if chapter.kind == "rho":
        return "\n\n".join(display for display, _ in rho_words())
    if not chapter.path or not chapter.path.exists():
        raise FileNotFoundError(chapter.path or chapter.id)
    return chapter.path.read_text(encoding="utf-8").strip()


def title_for(chapter: Chapter, raw: str) -> str:
    if chapter.title:
        return chapter.title
    match = re.search(r"^#\s+(.+?)\s*$", raw, re.M)
    if match:
        return re.sub(r"\s+\[[^\]]+\]\s*$", "", match.group(1)).strip()
    return chapter.id.replace("-", " ").title()


def strip_first_title(raw: str) -> str:
    return re.sub(r"^\s*#\s+.+?\n+", "", raw, count=1)


def render_poem(raw: str) -> str:
    clean = re.sub(r"<!--.*?-->", "", strip_first_title(raw), flags=re.S).strip()
    clean = re.sub(r"^---+\s*$", "◇", clean, flags=re.M)
    return f'<div class="verse">{html.escape(clean)}</div>'


def render_rho() -> str:
    entries = []
    for index, (display, original) in enumerate(rho_words(), 1):
        entries.append(
            '<li class="rho-word">'
            f'<span class="rho-index">{index:02d}</span>'
            f'<span class="rho-reversed">{html.escape(display)}</span>'
            f'<span class="rho-reveal">{html.escape(original)}</span>'
            "</li>"
        )
    return (
        '<p class="chapter-deck">Forty definition pages gathered into one continuous field. '
        "Hold or focus a word to reveal its carried orientation.</p>"
        f'<ol class="rho-run">{"".join(entries)}</ol>'
    )


def render_dedication(raw: str) -> str:
    paragraphs = [
        f"<p>{html.escape(line.strip())}</p>"
        for line in raw.splitlines()
        if line.strip()
    ]
    return f'<div class="dedication">{"".join(paragraphs)}</div>'


def render_markdown(raw: str) -> str:
    clean = re.sub(r"<!--.*?-->", "", strip_first_title(raw), flags=re.S).strip()
    return markdown.markdown(
        clean,
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )


def chapter_html(chapter: Chapter, raw: str) -> str:
    if chapter.kind == "poem":
        return render_poem(raw)
    if chapter.kind == "rho":
        return render_rho()
    if chapter.kind == "dedication":
        return render_dedication(raw)
    return render_markdown(raw)


def source_label(chapter: Chapter) -> str:
    if chapter.kind == "rho":
        return "src/003_rho/rho_definition_words.py"
    if chapter.path:
        return str(chapter.path.relative_to(ROOT))
    return ""


def reading_words(raw: str) -> int:
    clean = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    clean = re.sub(r"```.*?```", "", clean, flags=re.S)
    return len(re.findall(r"\b[\w’'-]+\b", clean, flags=re.UNICODE))


def audio_url(chapter: Chapter) -> str | None:
    path = AUDIO / f"{chapter.id}.mp3"
    return f"/book/audio/{chapter.id}.mp3" if path.exists() and path.stat().st_size > 1000 else None


def cue_url(chapter: Chapter) -> str | None:
    path = AUDIO / f"{chapter.id}.cues.json"
    return f"/book/audio/{chapter.id}.cues.json" if path.exists() else None


def publish_audio() -> None:
    WEB_AUDIO.mkdir(parents=True, exist_ok=True)
    expected: set[str] = set()
    for chapter in CHAPTERS:
        for suffix in (".mp3", ".cues.json"):
            src = AUDIO / f"{chapter.id}{suffix}"
            if not src.exists():
                continue
            dest = WEB_AUDIO / src.name
            expected.add(dest.name)
            if dest.exists() or dest.is_symlink():
                dest.unlink()
            try:
                dest.hardlink_to(src)
            except OSError:
                shutil.copy2(src, dest)
    for stale in WEB_AUDIO.iterdir() if WEB_AUDIO.exists() else []:
        if stale.is_file() and stale.name not in expected:
            stale.unlink()


def build() -> None:
    payload = []
    for index, chapter in enumerate(CHAPTERS):
        raw = raw_for(chapter)
        title = title_for(chapter, raw)
        words = reading_words(raw)
        payload.append(
            {
                "id": chapter.id,
                "index": index,
                "label": chapter.label,
                "title": title,
                "kind": chapter.kind,
                "source": source_label(chapter),
                "words": words,
                "minutes": max(1, round(words / 210)),
                "html": chapter_html(chapter, raw),
                "audio": audio_url(chapter),
                "cues": cue_url(chapter),
            }
        )
    publish_audio()
    WEB_BOOK.mkdir(parents=True, exist_ok=True)
    out = WEB_BOOK / "chapters.json"
    out.write_text(
        json.dumps(
            {
                "title": "REALITY_USER_MANUAL",
                "phase": "Pre-Phase 2",
                "narrator": "The Narrator · ElevenLabs",
                "chapters": payload,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"✓ {out} · {len(payload)} chapter pages · {sum(x['words'] for x in payload):,} words")


def speech_text(raw: str, title: str, kind: str) -> str:
    if kind == "rho":
        words = [original for _, original in rho_words()]
        return title + ". " + ". ".join(words) + "."

    text = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    text = re.sub(
        r"```(?:[^\n]*)\n(.*?)```",
        lambda m: " Code listing. " + re.sub(r"\s+", " ", m.group(1)).strip() + " End code listing. ",
        text,
        flags=re.S,
    )
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    text = text.replace("**", "").replace("__", "").replace("*", "")
    text = re.sub(
        r"^\s*\|(.+)\|\s*$",
        lambda m: ". ".join(cell.strip() for cell in m.group(1).split("|")) + ".",
        text,
        flags=re.M,
    )
    text = re.sub(r"^\s*[-:| ]{3,}\s*$", "", text, flags=re.M)
    text = re.sub(r"^---+\s*$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def speech_blocks(text: str, limit: int = 3200) -> list[str]:
    paragraphs = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    blocks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if not paragraph:
            continue
        if len(current) + len(paragraph) + 2 <= limit:
            current = f"{current}\n\n{paragraph}".strip()
            continue
        if current:
            blocks.append(current)
            current = ""
        while len(paragraph) > limit:
            cut = paragraph.rfind(". ", 0, limit)
            if cut < limit // 2:
                cut = paragraph.rfind(" ", 0, limit)
            if cut <= 0:
                cut = limit
            else:
                cut += 1
            blocks.append(paragraph[:cut].strip())
            paragraph = paragraph[cut:].strip()
        current = paragraph
    if current:
        blocks.append(current)
    return blocks


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def generate_audio(only: set[str] | None = None) -> None:
    sys.path.insert(0, str(ROOT / "tools"))
    import generate_audio as ga

    AUDIO.mkdir(parents=True, exist_ok=True)
    voice = ga.VOICE_MAP["The Narrator"]
    for chapter in CHAPTERS:
        if only and chapter.id not in only:
            continue
        raw = raw_for(chapter)
        title = title_for(chapter, raw)
        blocks = speech_blocks(speech_text(raw, title, chapter.kind))
        files: list[Path] = []
        cue_rows: list[dict] = []
        now = 0.0
        print(f"\n── {chapter.label} · {title} · {len(blocks)} narration blocks")
        for block in blocks:
            paths = ga.tts("The Narrator", block, voice)
            for path in paths:
                duration = probe_duration(path)
                if duration <= 0:
                    continue
                files.append(path)
                cue_rows.append(
                    {
                        "start": now,
                        "end": now + duration,
                        "speaker": "The Narrator",
                        "text": block,
                    }
                )
                now += duration
        if not files:
            raise SystemExit(f"No narration produced for {chapter.id}")
        target = AUDIO / f"{chapter.id}.mp3"
        if not ga.concatenate(files, target):
            raise SystemExit(f"Could not concatenate {chapter.id}")
        (AUDIO / f"{chapter.id}.cues.json").write_text(
            json.dumps({"id": chapter.id, "cues": cue_rows}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"✓ {target} · {now / 60:.1f} min")
    build()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "audio"), nargs="?", default="build")
    parser.add_argument("--only", help="comma-separated chapter ids")
    args = parser.parse_args()
    if args.command == "audio":
        only = {item.strip() for item in (args.only or "").split(",") if item.strip()} or None
        generate_audio(only)
    else:
        build()


if __name__ == "__main__":
    main()

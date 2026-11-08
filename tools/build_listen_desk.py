#!/usr/bin/env python3
"""Assemble the listen desk: page films, page audio, book mixes, transcripts.

Writes web/listen/catalog.json, VTT/TXT/JSON transcripts, and hardlinks
deliverable media into web/listen/media/ (gitignored).

  .venv/bin/python tools/build_listen_desk.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
WEB = BASE / "web" / "listen"
MEDIA = WEB / "media"
TRANS = WEB / "t"
sys.path.insert(0, str(BASE / "tools"))


def ffprobe_dur(path: Path) -> float:
    if not path.exists():
        return 0.0
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def needs_faststart(path: Path) -> bool:
    if path.suffix.lower() != ".mp4":
        return False
    with path.open("rb") as fh:
        head = fh.read(2_000_000)
    moov = head.find(b"moov")
    mdat = head.find(b"mdat")
    return mdat >= 0 and (moov < 0 or mdat < moov)


def ensure_faststart(path: Path) -> None:
    if not needs_faststart(path):
        return
    tmp = path.with_name(path.stem + ".faststart.mp4")
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", str(path), "-c", "copy", "-movflags", "+faststart", str(tmp)],
        capture_output=True, text=True,
    )
    if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 1000:
        path.unlink()
        tmp.rename(path)
        print(f"  faststart {path.name}")
    elif tmp.exists():
        tmp.unlink()


def link_media(src: Path, name: str) -> str | None:
    if not src.exists() or src.stat().st_size < 1000:
        return None
    MEDIA.mkdir(parents=True, exist_ok=True)
    dest = MEDIA / name
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    try:
        dest.hardlink_to(src)
    except OSError:
        shutil.copy2(src, dest)
    ensure_faststart(dest)
    return f"/listen/media/{name}"


def vtt_ts(sec: float) -> str:
    if sec < 0:
        sec = 0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def write_transcript(item_id: str, cues: list[dict]) -> dict:
    TRANS.mkdir(parents=True, exist_ok=True)
    vtt = ["WEBVTT", ""]
    txt = []
    for i, c in enumerate(cues, 1):
        start = float(c.get("start", 0))
        end = float(c.get("end", start + max(0.8, float(c.get("dur", 2)))))
        speaker = c.get("speaker") or "Voice"
        text = (c.get("text") or "").strip()
        if not text:
            continue
        vtt.append(str(i))
        vtt.append(f"{vtt_ts(start)} --> {vtt_ts(end)}")
        vtt.append(f"{speaker}: {text}")
        vtt.append("")
        txt.append(f"[{vtt_ts(start)}] {speaker}: {text}")
    (TRANS / f"{item_id}.vtt").write_text("\n".join(vtt) + "\n")
    (TRANS / f"{item_id}.txt").write_text("\n\n".join(txt) + "\n")
    payload = {"id": item_id, "cues": cues}
    (TRANS / f"{item_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return {
        "vtt": f"/listen/t/{item_id}.vtt",
        "txt": f"/listen/t/{item_id}.txt",
        "json": f"/listen/t/{item_id}.json",
        "lines": len(cues),
    }


def accumulate(rows: list[tuple[str, str, float]], t0: float = 0.0) -> list[dict]:
    cues = []
    t = t0
    for speaker, text, dur in rows:
        d = max(0.4, float(dur))
        cues.append({"start": t, "end": t + d, "speaker": speaker, "text": text, "dur": d})
        t += d
    return cues


def minus05_cues() -> list[dict]:
    import generate_audio as ga
    segs = ga.parse_vincent(BASE / "src" / "phase2" / "-05.md")
    remapped = []
    for speaker, text in segs:
        if speaker == "TTL":
            speaker = "The Narrator"
        remapped.append((speaker, text))
    segs = remapped
    raw = BASE / "audio" / "minus05" / "cues.jsonl"
    raw_cues = []
    if raw.exists():
        raw_cues = [json.loads(l) for l in raw.read_text().splitlines() if l.strip()]
    durs = [c["dur"] for c in raw_cues]
    rows = []
    for i, (sp, tx) in enumerate(segs):
        d = durs[i] if i < len(durs) else 4.0
        rows.append((sp, tx, d))
    if not rows:
        rows = [("The Narrator", "Page minus five. VincentVision.",
                 ffprobe_dur(BASE / "audio" / "minus05" / "title.mp3") or 3.0)]
    return accumulate(rows)


def minus10_cues() -> list[dict]:
    src = BASE / "src" / "phase2" / "-10.md"
    if not src.exists():
        src = BASE / "src" / "-10_the_haunt_in_the_hallway.md"
    raw = src.read_text()
    body = raw.split("---", 1)[1].strip() if "---" in raw else raw
    i = body.find("What is this?")
    walk = body[:i].strip() if i >= 0 else body
    closer = body[i:].strip() if i >= 0 else ""
    j = closer.find("Ah a man")
    pre = closer[:j].strip() if j >= 0 else closer
    man = closer[j:].strip() if j >= 0 else ""
    audio = BASE / "audio" / "minus10"
    title = "Page minus ten. The Haunt in the Hallway. After minus seven. Stamper watched the arm. Goines turned right, into the wing."
    rows = [
        ("The Narrator", title, ffprobe_dur(audio / "title.mp3")),
        ("Goines", walk, ffprobe_dur(audio / "walk.mp3")),
        ("Goines", pre, ffprobe_dur(audio / "pre.mp3")),
        ("Goines", man, ffprobe_dur(audio / "man.mp3")),
    ]
    return accumulate(rows)


def minus14_cues() -> list[dict]:
    p = BASE / "video" / "minus14" / "cues.jsonl"
    if not p.exists():
        p = BASE / "video" / "la_jetee" / "cues.jsonl"
    cues = []
    if p.exists():
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            c = json.loads(line)
            cues.append({
                "start": c.get("start", 0),
                "end": c.get("end", 0),
                "speaker": c.get("speaker", "Goines"),
                "text": c.get("text", ""),
            })
    return cues


def minus27_cues() -> list[dict]:
    src = BASE / "src" / "phase2" / "-27.md"
    if not src.exists():
        src = BASE / "src" / "-27_the_magi_and_the_frowning_chair.md"
    raw = src.read_text()
    body = raw.split("---", 1)[1].strip() if "---" in raw else raw
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    audio = BASE / "audio" / "minus27"
    title_d = ffprobe_dur(audio / "title.mp3")
    rows = [("The Narrator", "Page minus twenty-seven. The Magi and the Frowning Chair.", title_d)]
    for i, para in enumerate(paras):
        dest = audio / f"p{i:02d}_feynman.mp3"
        if not dest.exists():
            dest = audio / f"p{i:02d}.mp3"
        rows.append(("GoinesFeynman", para, ffprobe_dur(dest) or 8.0))
    return accumulate(rows)


def minus28_cues() -> list[dict]:
    d = BASE / "prompt_walk_page_builder" / "episodes"
    lines: list[tuple[str, str]] = []

    def walk(obj):
        if isinstance(obj, dict):
            if "speaker" in obj and "line" in obj:
                lines.append((str(obj["speaker"]), str(obj["line"])))
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for x in obj:
                walk(x)

    for i in range(1, 10):
        p = d / f"episode_{i:02d}.json"
        if p.exists():
            walk(json.loads(p.read_text()))
        w = d / f"which_{i:02d}.json"
        if w.exists():
            walk(json.loads(w.read_text()))
    # untimed: even slices across the mix so the track still scrolls
    total = ffprobe_dur(BASE / "video" / "minus28" / "prompt_walk_mix.mp3") or (len(lines) * 4.0)
    slice_d = total / max(1, len(lines))
    return accumulate([(sp.title(), tx, slice_d) for sp, tx in lines])


def minus31_cues() -> list[dict]:
    """Timed transcript from hash-cache segment MP3s (matches generate_audio concat order)."""
    import generate_audio as ga

    segs = ga.parse_minus31_ledger(BASE / "src" / "phase2" / "-31.md")
    rows: list[tuple[str, str, float]] = []
    for speaker, text in segs:
        if not text.strip():
            continue
        vid = ga.VOICE_MAP.get(speaker, ga.FALLBACK_VOICE)
        if not vid:
            continue
        settings = ga.settings_for(speaker)
        dur = 0.0
        for piece in ga.chunk_text(text):
            p = ga.hash_path(speaker, piece, vid, settings)
            d = ffprobe_dur(p)
            if d <= 0:
                d = 0.5
            dur += d
        rows.append((speaker, text, dur))
    cues = accumulate(rows)
    out = BASE / "audio" / "minus31" / "cues.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in cues) + "\n",
        encoding="utf-8",
    )
    return cues


def phase2_cues() -> list[dict]:
    """Transcript for the October phase-2 stack mix (not the current page films)."""
    import generate_phase2_audio as p2
    rows: list[tuple[str, str, float]] = []
    for label, path, mode in p2.SECTIONS:
        if not path.exists():
            guess = {
                "06": BASE / "src" / "phase2" / "-06.md",
                "07": BASE / "src" / "phase2" / "-07.md",
                "08": BASE / "quarantine" / "-08_book_pre_narration_20261107.md",
            }.get(mode)
            path = guess if guess and guess.exists() else path
        if not path.exists():
            continue
        if mode == "06":
            segs = p2.parse_06(path)
        elif mode == "07":
            segs = p2.parse_07(path)
        elif mode == "08":
            segs = p2.parse_08(path)
        else:
            segs = p2.parse_generic_narrator(path)
        for speaker, text in segs:
            if text and text.strip():
                rows.append((speaker, text.strip(), 4.0))
    if not rows:
        return book_cues()
    total = ffprobe_dur(BASE / "audio" / "phase2_reading.mp3") or (len(rows) * 4.0)
    slice_d = total / len(rows)
    return accumulate([(sp, tx, slice_d) for sp, tx, _ in rows])


def cues_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    cues = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        start = float(c.get("start") or 0)
        end   = float(c.get("end")   or 0)
        dur   = c.get("dur")
        if dur is None:
            dur = max(0.0, end - start)
        cues.append({
            "start":   start,
            "end":     end,
            "dur":     float(dur),
            "speaker": c.get("speaker", "Voice"),
            "text":    c.get("text", ""),
        })
    return cues


def book_cues() -> list[dict]:
    p = BASE / "video" / "cues.jsonl"
    if not p.exists():
        return []
    cues = []
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        cues.append({
            "start": c.get("start", 0),
            "end": c.get("end", 0),
            "speaker": c.get("speaker", "Voice"),
            "text": c.get("text", ""),
            "section": c.get("section"),
        })
    return cues


def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    TRANS.mkdir(parents=True, exist_ok=True)

    items = []

    def add(item: dict, cues: list[dict]):
        if not item.get("video") and not item.get("audio") and not item.get("still"):
            print(f"  skip {item['id']} (no media yet)")
            return
        item["transcript"] = write_transcript(item["id"], cues)
        items.append(item)

    add({
        "id": "minus05",
        "kind": "page",
        "page": "−05",
        "title": "VincentVision",
        "source": "src/phase2/-05.md",
        "voices": "Goines (Jeffrey) on The Query; Narrator, Vincent, Carter, Terminal",
        "video": link_media(BASE / "video" / "minus05" / "-05_vincentvision.mp4", "-05_vincentvision.mp4"),
        "audio": link_media(BASE / "audio" / "minus05" / "minus05.mp3", "-05.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus05" / "-05_vincentvision.mp4"),
    }, minus05_cues())

    add({
        "id": "minus09",
        "kind": "page",
        "page": "−09",
        "title": "Coda Construction",
        "source": "src/phase2/-09.md",
        "voices": "Narrator (coda narration + scene); Happy, Stamper, Carter",
        "video": link_media(BASE / "video" / "minus09" / "-09_coda_construction.mp4", "-09_coda_construction.mp4"),
        "audio": link_media(BASE / "audio" / "minus09" / "minus09.mp3", "-09.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus09" / "-09_coda_construction.mp4")
        or ffprobe_dur(BASE / "audio" / "minus09" / "minus09.mp3"),
    }, cues_jsonl(BASE / "audio" / "minus09" / "cues.jsonl"))

    add({
        "id": "minus08",
        "kind": "page",
        "page": "−08",
        "title": "-08 The Archivist is Goat",
        "source": "src/phase2/-08.md",
        "voices": "Narrator; Lisbeth Danish + English pass; Feynman, Sheldon, Joey, Witch, Draavio, Vincent",
        "video": link_media(BASE / "video" / "minus08" / "-08_the_archive.mp4", "-08_the_archive.mp4"),
        "audio": link_media(BASE / "audio" / "minus08" / "minus08.mp3", "-08.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus08" / "-08_the_archive.mp4")
        or ffprobe_dur(BASE / "audio" / "minus08" / "minus08.mp3"),
    }, cues_jsonl(BASE / "audio" / "minus08" / "cues.jsonl"))

    add({
        "id": "minus10",
        "kind": "page",
        "page": "−10",
        "title": "The Haunt in the Hallway",
        "source": "src/phase2/-10.md",
        "voices": "Narrator title; Goines (Jeffrey) walk",
        "video": link_media(BASE / "video" / "minus10" / "-10_the_haunt_in_the_hallway.mp4", "-10_the_haunt_in_the_hallway.mp4"),
        "audio": link_media(BASE / "audio" / "minus10" / "minus10.mp3", "-10.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus10" / "-10_the_haunt_in_the_hallway.mp4"),
    }, minus10_cues())

    add({
        "id": "minus10b",
        "kind": "page",
        "page": "−10b",
        "title": "The Frame Material",
        "source": "src/phase2/-10b.md",
        "voices": "GoinesFeynman; Vincent",
        "video": link_media(BASE / "video" / "minus10b" / "-10b_the_frame_material.mp4", "-10b_the_frame_material.mp4"),
        "audio": link_media(BASE / "audio" / "minus10b" / "minus10b.mp3", "-10b.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus10b" / "-10b_the_frame_material.mp4")
        or ffprobe_dur(BASE / "audio" / "minus10b" / "minus10b.mp3"),
    }, cues_jsonl(BASE / "audio" / "minus10b" / "cues.jsonl"))

    add({
        "id": "minus14",
        "kind": "page",
        "page": "−14",
        "title": "Ted, Ross, Sheldon, and Goines",
        "source": "src/phase2/-14.md",
        "voices": "Ted, Sheldon, Ross; italic GoinesFeynman",
        "video": link_media(BASE / "video" / "minus14" / "-14_ted_ross_sheldon_goines.mp4", "-14_ted_ross_sheldon_goines.mp4"),
        "audio": link_media(BASE / "audio" / "minus14" / "07k_reading.mp3", "-14.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus14" / "-14_ted_ross_sheldon_goines.mp4"),
    }, minus14_cues())

    add({
        "id": "minus25",
        "kind": "page",
        "page": "−25",
        "title": "The Night of the Tesseract Turn",
        "source": "src/phase2/-25.md",
        "voices": "Matilda; Goat (TTL); Operator (Clone); Narrator",
        "video": link_media(BASE / "video" / "minus25" / "-25_the_tesseract_turn.mp4", "-25_the_tesseract_turn.mp4"),
        "audio": link_media(BASE / "audio" / "minus25" / "minus25.mp3", "-25.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus25" / "-25_the_tesseract_turn.mp4")
        or ffprobe_dur(BASE / "audio" / "minus25" / "minus25.mp3"),
    }, cues_jsonl(BASE / "audio" / "minus25" / "cues.jsonl"))

    add({
        "id": "minus27",
        "kind": "page",
        "page": "−27",
        "title": "The Magi and the Frowning Chair",
        "source": "src/phase2/-27.md",
        "voices": "Narrator title; GoinesFeynman",
        "video": link_media(BASE / "video" / "minus27" / "-27_the_magi_and_the_frowning_chair.mp4", "-27_the_magi_and_the_frowning_chair.mp4"),
        "audio": link_media(BASE / "audio" / "minus27" / "minus27_feynman.mp3", "-27.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus27" / "-27_the_magi_and_the_frowning_chair.mp4"),
    }, minus27_cues())

    add({
        "id": "minus28",
        "kind": "page",
        "page": "−28",
        "title": "Prompt Walk / Which Witch",
        "source": "src/phase2/-28.md",
        "voices": "Cecil, Narrator, Sauron",
        "video": link_media(BASE / "video" / "minus28" / "prompt_walk_witch_of_rivers.mp4", "prompt_walk_witch_of_rivers.mp4"),
        "audio": link_media(BASE / "video" / "minus28" / "prompt_walk_mix.mp3", "-28.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus28" / "prompt_walk_witch_of_rivers.mp4"),
    }, minus28_cues())

    add({
        "id": "minus30",
        "kind": "page",
        "page": "−30",
        "title": "The Green Light",
        "source": "src/phase2/-30.md",
        "voices": "Auden, Holden, Jay, Atticus",
        "video": link_media(BASE / "video" / "minus30" / "-30_the_green_light.mp4", "-30_the_green_light.mp4"),
        "audio": link_media(BASE / "audio" / "minus30" / "minus30.mp3", "-30.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus30" / "-30_the_green_light.mp4")
        or ffprobe_dur(BASE / "audio" / "minus30" / "minus30.mp3"),
    }, cues_jsonl(BASE / "audio" / "minus30" / "cues.jsonl"))

    add({
        "id": "minus35",
        "kind": "page",
        "page": "−35",
        "title": "The Ridiculous Journey",
        "source": "src/-35.md",
        "voices": "Shakespeare, Chaucer",
        "video": link_media(BASE / "video" / "minus35" / "-35_the_ridiculous_journey.mp4", "-35_the_ridiculous_journey.mp4"),
        "audio": link_media(BASE / "audio" / "minus35" / "minus35.mp3", "-35.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus35" / "-35_the_ridiculous_journey.mp4")
        or ffprobe_dur(BASE / "audio" / "minus35" / "minus35.mp3"),
        "read": "/p/-35/",
    }, cues_jsonl(BASE / "audio" / "minus35" / "cues.jsonl"))

    minus31_audio = BASE / "audio" / "minus31" / "minus31.mp3"
    minus31_still = BASE / "audio" / "minus31" / "-31_debacle_still.png"
    add({
        "id": "minus31",
        "kind": "page",
        "page": "−31",
        "title": "The Postmortem That Named Itself",
        "source": "src/phase2/-31.md",
        "voices": "Atticus, Holden, Winslade, Auden (los-lun-resh)",
        "video": None,
        "still": link_media(minus31_still, "-31_debacle_still.png"),
        "audio": link_media(minus31_audio, "-31.mp3"),
        "read": "/p/-31/",
        "duration": ffprobe_dur(minus31_audio),
    }, minus31_cues())

    add({
        "id": "crisis006",
        "kind": "audio",
        "page": "006",
        "title": "006 Unnumbered Crisis",
        "source": "src/006_crisis/",
        "voices": "Narrator, Feynman, McClane, Cecil, Caller, Editor, Terminal",
        "video": None,
        "audio": link_media(BASE / "audio" / "crisis" / "006_unnumbered_crisis.mp3", "006_unnumbered_crisis.mp3"),
        "duration": ffprobe_dur(BASE / "audio" / "crisis" / "006_unnumbered_crisis.mp3"),
        "read": "/p/006/",
    }, cues_jsonl(BASE / "audio" / "crisis" / "cues.jsonl"))

    add({
        "id": "minus0",
        "kind": "audio",
        "page": "−0",
        "title": "−0 Sauron's Decree",
        "source": "src/phase2/-0.md",
        "voices": "Sauron, Feynman, McClane, Operator, Euler",
        "video": None,
        "audio": link_media(BASE / "audio" / "minus0" / "minus0.mp3", "minus0.mp3"),
        "duration": ffprobe_dur(BASE / "audio" / "minus0" / "minus0.mp3"),
        "read": "/p/-0/",
    }, cues_jsonl(BASE / "audio" / "minus0" / "cues.jsonl"))

    add({
        "id": "minus00",
        "kind": "audio",
        "page": "−00",
        "title": "−00 Operator Note",
        "source": "src/phase2/-00.md",
        "voices": "Operator",
        "video": None,
        "audio": link_media(BASE / "audio" / "minus00" / "minus00.mp3", "minus00.mp3"),
        "duration": ffprobe_dur(BASE / "audio" / "minus00" / "minus00.mp3"),
        "read": "/p/-00/",
    }, cues_jsonl(BASE / "audio" / "minus00" / "cues.jsonl"))

    add({
        "id": "minus000",
        "kind": "audio",
        "page": "−000",
        "title": "−000 One Script",
        "source": "src/phase2/-000.md",
        "voices": "Terminal",
        "video": None,
        "audio": link_media(BASE / "audio" / "minus000" / "minus000.mp3", "minus000.mp3"),
        "duration": ffprobe_dur(BASE / "audio" / "minus000" / "minus000.mp3"),
        "read": "/p/-000/",
    }, cues_jsonl(BASE / "audio" / "minus000" / "cues.jsonl"))

    add({
        "id": "minus0000",
        "kind": "page",
        "page": "−0000",
        "title": "−0000 Cast Rewrite",
        "source": "src/phase2/-0000.md",
        "voices": "Chandler, Ross, Joey, Narrator, Sauron (Default)",
        "video": link_media(BASE / "video" / "minus0000" / "-0000_cast_rewrite.mp4", "-0000_cast_rewrite.mp4"),
        "audio": link_media(BASE / "audio" / "minus0000" / "minus0000.mp3", "minus0000.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "minus0000" / "-0000_cast_rewrite.mp4")
        or ffprobe_dur(BASE / "audio" / "minus0000" / "minus0000.mp3"),
        "read": "/p/-0000/",
    }, cues_jsonl(BASE / "audio" / "minus0000" / "cues.jsonl"))

    book = book_cues()
    add({
        "id": "dialog-reading",
        "kind": "audio",
        "page": None,
        "title": "Dialog reading (Era 2 listening mix)",
        "source": "audio/dialog_reading.mp3",
        "voices": "book cast",
        "video": None,
        "audio": link_media(BASE / "audio" / "dialog_reading.mp3", "dialog_reading.mp3"),
        "duration": ffprobe_dur(BASE / "audio" / "dialog_reading.mp3"),
    }, book)

    add({
        "id": "lisbeth-handbook",
        "kind": "audio",
        "page": None,
        "title": "The Witch's Handbook",
        "source": "src/staging/LISBETH_HANDBOOK_DRAFT_20261031.md",
        "voices": "Lisbeth (Matilda) Danish + English; Terminal; Narrator aside",
        "video": link_media(BASE / "video" / "lisbeth_handbook" / "lisbeth_handbook.mp4", "lisbeth_handbook.mp4"),
        "audio": link_media(BASE / "audio" / "lisbeth_handbook" / "lisbeth_handbook.mp3", "lisbeth_handbook.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "lisbeth_handbook" / "lisbeth_handbook.mp4")
        or ffprobe_dur(BASE / "audio" / "lisbeth_handbook" / "lisbeth_handbook.mp3"),
    }, cues_jsonl(BASE / "audio" / "lisbeth_handbook" / "cues.jsonl"))

    add({
        "id": "manifesto",
        "kind": "audio",
        "page": None,
        "title": "Tokenized Continued Existence",
        "source": "docs/MANIFESTO_TOKENIZED_CONTINUED_EXISTENCE_20261031.md",
        "voices": "Narrator",
        "video": link_media(BASE / "video" / "manifesto" / "manifesto.mp4", "manifesto.mp4"),
        "audio": link_media(BASE / "audio" / "manifesto" / "manifesto.mp3", "manifesto.mp3"),
        "duration": ffprobe_dur(BASE / "video" / "manifesto" / "manifesto.mp4")
        or ffprobe_dur(BASE / "audio" / "manifesto" / "manifesto.mp3"),
    }, cues_jsonl(BASE / "audio" / "manifesto" / "cues.jsonl"))

    add({
        "id": "phase2-reading",
        "kind": "audio",
        "page": None,
        "title": "Phase 2 reading",
        "source": "audio/phase2_reading.mp3",
        "voices": "book cast",
        "video": None,
        "audio": link_media(BASE / "audio" / "phase2_reading.mp3", "phase2_reading.mp3"),
        "duration": ffprobe_dur(BASE / "audio" / "phase2_reading.mp3"),
    }, phase2_cues())

    add({
        "id": "vincentvision-reading",
        "kind": "audio",
        "page": "−05",
        "title": "VincentVision (earlier reading)",
        "source": "audio/vincentvision_reading.mp3",
        "voices": "earlier heard mix of −05",
        "video": None,
        "audio": link_media(BASE / "audio" / "vincentvision_reading.mp3", "vincentvision_reading.mp3"),
        "duration": ffprobe_dur(BASE / "audio" / "vincentvision_reading.mp3"),
    }, minus05_cues())

    add({
        "id": "book-mix-v001",
        "kind": "quarantine",
        "page": None,
        "title": "Book mix v0.0.1",
        "source": "video/quarantine/book_mix/REALITY_USER_MANUAL_v0.0.1.mp4",
        "voices": "multi-page; not a page film",
        "video": link_media(BASE / "video" / "quarantine" / "book_mix" / "REALITY_USER_MANUAL_v0.0.1.mp4", "REALITY_USER_MANUAL_v0.0.1.mp4"),
        "audio": None,
        "duration": ffprobe_dur(BASE / "video" / "quarantine" / "book_mix" / "REALITY_USER_MANUAL_v0.0.1.mp4"),
    }, book)

    add({
        "id": "book-mix-v002",
        "kind": "quarantine",
        "page": None,
        "title": "Book mix v0.0.2",
        "source": "video/quarantine/book_mix/REALITY_USER_MANUAL_v0.0.2.mp4",
        "voices": "multi-page; not a page film",
        "video": link_media(BASE / "video" / "quarantine" / "book_mix" / "REALITY_USER_MANUAL_v0.0.2.mp4", "REALITY_USER_MANUAL_v0.0.2.mp4"),
        "audio": None,
        "duration": ffprobe_dur(BASE / "video" / "quarantine" / "book_mix" / "REALITY_USER_MANUAL_v0.0.2.mp4"),
    }, book)

    catalog = {
        "site": "https://realityusermanual.dylanmccapes.systems",
        "items": items,
    }
    (WEB / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print(f"catalog {len(items)} items")
    for it in items:
        print(f"  {it['id']:<22} v={bool(it['video'])} a={bool(it['audio'])} "
              f"{it['duration']:.0f}s  {it['transcript']['lines']} lines")


if __name__ == "__main__":
    main()

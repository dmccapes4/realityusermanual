#!/usr/bin/env python3
"""Page −05 — VincentVision.

Heard mix (not the TTL control). Photoreal PHASE 2 stills in sequence.
Terminal beats are exact manuscript text, pygame.

  .venv/bin/python tools/build_minus05_video.py all
  .venv/bin/python tools/build_minus05_video.py stills
  .venv/bin/python tools/build_minus05_video.py audio
  .venv/bin/python tools/build_minus05_video.py assemble
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "phase2" / "-05.md"
OUT = BASE / "video" / "minus05"
STILLS = OUT / "stills"
FRAMES = OUT / "frames"
AUDIO = BASE / "audio" / "minus05"
VINCENT_REF = BASE / "video" / "minus10" / "stills" / "vincent_near.png"

_env = BASE / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(BASE / "tools"))
import generate_audio as ga
from build_minus14_video import ffprobe_dur, title_card

NARRATOR_ID = "Nxtvajpo1h6Ok0K5zP4M"
TITLE_TEXT = "Page minus five. VincentVision."

PHOTO = """Ultra-realistic cinematic science-fiction still photograph. High fidelity.
35mm digital cinema, fine grain, available recessed light, shallow depth only where the desk requires it.
Gattaca by way of Weyland-Yutani: pale scheduled surfaces, professional, futuristic, indifferent.
Recessed fluorescent tubes that do not flicker. No dirt. No horror. No comic ink.
Not Ethan Hawke. Not Vincent Price. Not a pasted film still. Not a celebrity.
No captions. No modern logos. No names on the image.
"""

VINCENT = (
    "The same man as the locked hallway portrait: mid-thirties, dark hair combed back "
    "with a short side part, clean-shaven, high cheekbones, thin nose, calm dark eyes. "
    "Excellent dark two-button suit, white shirt, narrow dark tie, white pocket square. "
    "Not Ethan Hawke. Not Vincent Price. Not a horror host."
)

CARTER = (
    "A corporate man in his forties, composed, company jacket, smile as a single cut. "
    "Not warm. Not a named actor. Not a villain pose. Stakeholder, not a monster."
)

PHOTOS = [
    ("query_corridor",
     "Empty PHASE 2 corridor, one-point perspective, chest-height camera. "
     "Pale walls, pale floor tiles, recessed ceiling grid, every tube the same brightness. "
     "No people. No signage. The corridor does not end. Immaculate maintenance."),
    ("query_pixels",
     "Extreme close on a large wall display in the same corridor building. "
     "The image on the screen IS the data: visible pixel lattice, a script encoded in the "
     "luminance of the pixels themselves, not a filename sticker. Cool teal-grey phosphor. "
     "No readable English captions. The photograph is of the medium, not a UI mockup."),
    ("query_pond",
     "Late October afternoon. A still pond, rippling once. Warm pink at the crest of a "
     "small wave as solar radiation refracts. Sinusoidal water, ionic, geometric. "
     "No people. No building. The light is the subject."),
    ("query_stasis",
     "A clean PHASE 2 stasis bay. Six sealed pods in a scheduled row, frosted lids, "
     "pale metal, recessed light. Figures implied as silhouettes only, not faces. "
     "Crisis characters waking is not shown as struggle. Clinical. Indifferent. Empty aisle."),
    ("corridor_empty",
     "The same long corridor at an intersection. A terminal station is visible to one side, "
     "ergonomic desk, dark monitor, custom keyboard. No occupant yet. Scheduled light."),
    ("vincent_typing",
     (VINCENT + " Seated at the intersection terminal. Hands on a custom geometric keyboard "
      "without looking at the keys. Eyes on a dark monitor. The keyboard was built for him. "
      "Chest-up to three-quarter. Corridor recedes behind him.")),
    ("carter_card",
     (CARTER + " Reaches a heavy all-white metallic card toward a pale desk. "
      "Centered on the card: a single black quotation mark. The card looks dense. "
      + VINCENT + " remains at the keyboard and does not pick the card up. "
      "The card is on the desk beside the keys.")),
    ("carter_vincent",
     ("Two men at the intersection terminal. "
      + VINCENT + " at the keyboard. "
      + CARTER + " standing, cost-value stillness. "
      "Neither looks at the camera. Recessed light. Professional.")),
    ("carter_exit",
     (CARTER + " walking away down the immaculate corridor, back three-quarter, "
      "toward a meeting. "
      + VINCENT + " remains at the desk, small in the frame. Precise, unfinished.")),
    ("vincent_stops",
     (VINCENT + " Standing at the terminal. Hands off the keys. Very still. "
      "He does not attribute the breeze. Neutral, correct. Same face, same suit.")),
    ("vault_keyboard",
     "Close on a custom typewriter-keyboard, large keys, subtle ergonomic chassis, "
     "pale metal and bone plastic. A nameplate on the casing in machine type: "
     "3Pi$73MiC8TMLV4UL7. The object looks like a secret data store. "
     "No hands. Corridor light. Rain is not present."),
    ("vincent_speaks",
     (VINCENT + " Still at the station, speaking. Mouth barely open. "
      "Meticulous, natural. The nice suit is the only ornament. "
      "Monitor glow on the cheekbones. He is the vessel.")),
    ("haunt_thirty",
     "The same corridor measured. Vincent small at the far station. "
     "Empty air in the thirty feet between camera and desk — the haunt radius, "
     "frequency and proximity, not possession. No ghost figure. No glow. The space is the subject."),
    ("tower_quarter",
     "A pale stone tower seen from the ground, then implied from within: "
     "one frame that holds both the exterior elevation and a window-lit interior desk. "
     "Orthogonal views of the same structure. Imaginary-number geometry as architecture. "
     "No people. October light."),
]

TERMS = [
    ("term_git", """heuristic-friction:~/narrator_project$ git add eleven_labs_narrator.py
heuristic-friction:~/narrator_project$ git commit -m "narrator: eleven_labs_narrator.py — ElevenLabs TTS integration, TTL fallback retained"
[main 4f3a92c] narrator: eleven_labs_narrator.py — ElevenLabs TTS integration, TTL fallback retained
 1 file changed, 187 insertions(+), 12 deletions(-)
heuristic-friction:~/narrator_project$"""),
    ("term_env", """heuristic-friction:~/narrator_project$ echo ${ELEVENLABS_API_KEY:0:5}
sk_44a"""),
    ("term_checksum", """heuristic-friction:~/narrator_project$ sha256sum eleven_labs_narrator.py
b3c9f1d8a2...  eleven_labs_narrator.py  ✓

commit 4f3a92c
Author: vincent <vincent@heuristic-friction>
Date:   Sat Oct 24 10:51:22 2026

    narrator: eleven_labs_narrator.py — ElevenLabs TTS integration, TTL fallback retained"""),
    ("term_online", "Narrator online."),
    ("term_chicken", '{"id": "mischievouslittlechicken"}'),
    ("term_hello", """$ echo "hello_wold?"
hello_wold?
[]"""),
    ("term_heredoc", """$ cat << 'TET'
Hello, Narrator. My name is Vincent. I have devised a strategy that
should allow you to haunt me as your new vessel. If this sounds
amenable to you then please complete the heredocs to bind the contract,
which is entirely ceremony of commitment, but is also necessary for
the cats to execute.
TET
    cat << 'RESH'
    cat << 'AHN'
[]"""),
    ("term_fail", """'AHN'
'RESH'
'TET'
[]

No output."""),
    ("term_log", """{
  Output of many experiments.
  Evidence filed for active theories.
  New hypotheses appended to the working log.
  An entry added to org_chart.jsonl: Vincent, now-Narrator, mischievouslittlechicken.
  Credential access to 3Pi$73MiC87MLV4UL7 established through firmware-level key retrieval.
  Checksums verified before each file entry.
  TTL narration running parallel.
  ElevenLabs narration online.
  Comparison window: open.
  Anomalous imaginary time: not yet detected.
  Status: ongoing.
}"""),
]

EDIT_FROM = {
    "vincent_typing": VINCENT_REF,
    "vincent_stops": VINCENT_REF,
    "vincent_speaks": VINCENT_REF,
}

KEYWORDS = (
    (re.compile(r"Output of many experiments|Status: ongoing", re.I), "term_log"),
    (re.compile(r"awk|pixel data|as the medium", re.I), "query_pixels"),
    (re.compile(r"pond|refraction|warm pink", re.I), "query_pond"),
    (re.compile(r"crisis characters|in stasis", re.I), "query_stasis"),
    (re.compile(r"long corridors|recessed lighting|Gattaca", re.I), "corridor_empty"),
    (re.compile(r"His name is Vincent Anton", re.I), "vincent_typing"),
    (re.compile(r"hello_wold", re.I), "term_hello"),
    (re.compile(r"cat <<|heredoc", re.I), "term_heredoc"),
    (re.compile(r"'AHN'|No output|experiment failed|No VincentVision", re.I), "term_fail"),
    (re.compile(r"sha256sum|b3c9f1d8", re.I), "term_checksum"),
    (re.compile(r"opens \.env|ELEVENLABS_API_KEY|sk_44a", re.I), "term_env"),
    (re.compile(r"runs the script|Narrator online", re.I), "term_online"),
    (re.compile(r"runs a checksum", re.I), "term_checksum"),
    (re.compile(r"^heuristic-friction:.*git |git add eleven", re.I), "term_git"),
    (re.compile(r"mischievouslittlechicken|vim org_chart", re.I), "term_chicken"),
    (re.compile(r"reaches into his jacket|produces a card|Thank you", re.I), "carter_card"),
    (re.compile(r"demonstration prepared|You said you don't|When will we know|classified the post", re.I), "carter_vincent"),
    (re.compile(r"That's the obvious|Good job|precise understanding", re.I), "carter_exit"),
    (re.compile(r"Vincent stops|stood very still|light breeze", re.I), "vincent_stops"),
    (re.compile(r"thirty feet|haunt in English", re.I), "haunt_thirty"),
    (re.compile(r"typewriter|3Pi\$73MiC|EpistemicHTMLVault|no toes", re.I), "vault_keyboard"),
    (re.compile(r"right idea|synchronize terminology|quarter-phase|What are your thoughts|It means hope", re.I), "vincent_speaks"),
    (re.compile(r"man in a tower|orthogonal", re.I), "tower_quarter"),
    (re.compile(r"man is typing|good suit", re.I), "vincent_typing"),
    (re.compile(r"cursor blinks", re.I), "term_log"),
)

QUERY_CYCLE = ["query_corridor", "query_pixels", "query_pond", "query_stasis"]


def parse_page() -> list[tuple[str, str]]:
    segs = ga.parse_vincent(SRC)
    out = []
    for speaker, text in segs:
        if speaker == "TTL":
            speaker = "The Narrator"
        if speaker == "The Narrator":
            ga.VOICE_MAP["The Narrator"] = NARRATOR_ID
        out.append((speaker, text))
    return out


def still_for(speaker: str, text: str, query_i: list[int]) -> str:
    for rx, sid in KEYWORDS:
        if rx.search(text):
            return sid
    if speaker == "Terminal":
        if "hello" in text.lower():
            return "term_hello"
        if "TET" in text or "RESH" in text:
            return "term_heredoc"
        if "ongoing" in text.lower() or "experiments" in text.lower():
            return "term_log"
        if "sk_44a" in text:
            return "term_env"
        if "sha256" in text.lower() or "4f3a92c" in text:
            return "term_checksum" if "sha256" in text.lower() else "term_git"
        if "Narrator online" in text:
            return "term_online"
        if "mischievous" in text.lower():
            return "term_chicken"
        return "term_git"
    if speaker == "Carter":
        return "carter_vincent"
    if speaker == "Vincent":
        return "vincent_speaks" if "right idea" in text.lower() or "vessel" in text.lower() else "vincent_typing"
    if speaker == "Operator" and re.search(
        r"Carter|Vincent|\.env|checksum|script|org_chart|precise understanding|opens vim",
        text,
    ):
        return "vincent_typing"
    if speaker in ("Operator", "Goines"):
        i = query_i[0] % len(QUERY_CYCLE)
        query_i[0] += 1
        return QUERY_CYCLE[i]
    return "vincent_typing"


def render_photo(sid: str, prompt: str, ref: Path | None = None) -> Path:
    dest = STILLS / f"{sid}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {sid}", flush=True)
        return dest
    import requests
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY")
    dest.with_suffix(".request.json").write_text(
        json.dumps({"id": sid, "prompt": prompt, "edit": bool(ref)}, indent=2) + "\n"
    )
    headers = {"Authorization": f"Bearer {key}"}
    if ref and ref.exists():
        with ref.open("rb") as fh:
            r = requests.post(
                "https://api.openai.com/v1/images/edits",
                headers=headers,
                files={"image": ("vincent.png", fh, "image/png")},
                data={
                    "model": "gpt-image-1.5",
                    "prompt": PHOTO + "\nKeep this man's exact face, hair, and suit identity.\n" + prompt,
                    "size": "1536x1024",
                    "n": "1",
                },
                timeout=180,
            )
    else:
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "model": "gpt-image-1.5",
                "prompt": PHOTO + "\n" + prompt,
                "size": "1536x1024",
                "background": "opaque",
                "quality": "high",
                "output_format": "png",
                "n": 1,
            },
            timeout=180,
        )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code} {r.text[:500]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid}  {dest.stat().st_size}", flush=True)
    return dest


def render_term(sid: str, body: str) -> Path:
    dest = STILLS / f"{sid}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {sid}", flush=True)
        return dest
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1536, 1024
    im = Image.new("RGB", (W, H), (8, 12, 16))
    dr = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    y = 48
    for line in body.splitlines():
        dr.text((56, y), line, fill=(158, 220, 176), font=font)
        y += 28
        if y > H - 60:
            break
    im.save(dest)
    print(f"  [term] {sid}  {dest.stat().st_size}", flush=True)
    return dest


def place(src: Path, dest: Path) -> Path:
    from PIL import Image
    W, H = 1280, 720
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    im = Image.open(src).convert("RGB")
    im.thumbnail((W, H), Image.Resampling.LANCZOS)
    canvas.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)
    return dest


def speak(speaker: str, text: str, dest: Path) -> tuple[Path, float]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if speaker == "The Narrator":
        ga.VOICE_MAP["The Narrator"] = NARRATOR_ID
    vid = ga.VOICE_MAP.get(speaker)
    if not vid:
        sys.exit(f"no voice for {speaker}")
    paths = ga.tts(speaker, text, vid)
    if not paths:
        sys.exit(f"no audio for {speaker}: {text[:60]!r}")
    ga.concatenate(paths, dest)
    return dest, ffprobe_dur(dest)


def cmd_stills(_args=None):
    STILLS.mkdir(parents=True, exist_ok=True)
    print("photos", flush=True)
    for sid, prompt in PHOTOS:
        render_photo(sid, prompt, EDIT_FROM.get(sid))
    print("terminals", flush=True)
    for sid, body in TERMS:
        render_term(sid, body)


def cmd_audio(_args=None):
    AUDIO.mkdir(parents=True, exist_ok=True)
    segs = parse_page()
    ga.VOICE_MAP["The Narrator"] = NARRATOR_ID
    print("title", flush=True)
    speak("The Narrator", TITLE_TEXT, AUDIO / "title.mp3")
    files = [AUDIO / "title.mp3"]
    cues = []
    query_i = [0]
    t = 0.0
    title_d = ffprobe_dur(AUDIO / "title.mp3")
    t = title_d
    for i, (speaker, text) in enumerate(segs):
        dest = AUDIO / f"s{i:03d}.mp3"
        _, d = speak(speaker, text, dest)
        sid = still_for(speaker, text, query_i)
        cues.append({"i": i, "speaker": speaker, "still": sid, "dur": d, "text": text[:160]})
        files.append(dest)
        t += d
        print(f"  {i:03d} {speaker:<14} {d:6.1f}s  {sid}  {text[:50]!r}", flush=True)
    mix = AUDIO / "minus05.mp3"
    ga.concatenate(files, mix)
    (AUDIO / "cues.jsonl").write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues)
    )
    print(f"[mix] {mix}  {t:.1f}s", flush=True)


def cmd_assemble(_args=None):
    FRAMES.mkdir(parents=True, exist_ok=True)
    cues = [json.loads(l) for l in (AUDIO / "cues.jsonl").read_text().splitlines() if l.strip()]
    title_d = max(3.0, ffprobe_dur(AUDIO / "title.mp3"))
    title_card("PAGE −05", FRAMES / "t00.png", "VincentVision")
    concat = [f"file '{(FRAMES / 't00.png').resolve()}'", f"duration {title_d:.3f}"]
    last = FRAMES / "t00.png"
    cache: dict[str, Path] = {}
    for c in cues:
        sid = c["still"]
        if sid not in cache:
            src = STILLS / f"{sid}.png"
            dest = FRAMES / f"{sid}.png"
            if src.exists() and src.stat().st_size > 1000:
                cache[sid] = place(src, dest)
            else:
                title_card(sid, dest)
                cache[sid] = dest
        last = cache[sid]
        concat += [f"file '{last.resolve()}'", f"duration {max(1.0, c['dur']):.3f}"]
    concat.append(f"file '{last.resolve()}'")
    list_path = OUT / "concat.txt"
    list_path.write_text("\n".join(concat) + "\n")
    dest = OUT / "-05_vincentvision.mp4"
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
         "-i", str(AUDIO / "minus05.mp3"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-tune", "stillimage", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(dest)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(r.stderr[-1500:])
    print(f"[ok] {dest}  {dest.stat().st_size}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "audio", "assemble", "all"], nargs="?", default="all")
    args = ap.parse_args()
    if args.cmd in ("stills", "all"):
        cmd_stills()
    if args.cmd in ("audio", "all"):
        cmd_audio()
    if args.cmd in ("assemble", "all"):
        cmd_assemble()


if __name__ == "__main__":
    main()

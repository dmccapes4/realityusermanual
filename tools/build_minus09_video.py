#!/usr/bin/env python3
"""Page −09 — Coda code + TUROV construction site.

Video: C source on screen while the Narrator reads spoken-code; TUROV sign;
then photoreal promo stills (pharma-ad cheer on a construction site).

  .venv/bin/python tools/build_minus09_video.py audio
  .venv/bin/python tools/build_minus09_video.py stills --render
  .venv/bin/python tools/build_minus09_video.py frames
  .venv/bin/python tools/build_minus09_video.py assemble
  .venv/bin/python tools/build_minus09_video.py all --render
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "phase2" / "-09.md"
CODA = BASE / "truth" / "coda.c"
AUDIO = BASE / "audio" / "minus09"
OUT = BASE / "video" / "minus09"
STILLS = OUT / "stills"
FRAMES = OUT / "frames"

_env = BASE / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

W, H, FPS = 1280, 720, 30
CODE_BG = (18, 22, 28)
CODE_FG = (210, 220, 230)
CODE_DIM = (120, 140, 160)
CODE_HI = (255, 230, 140)
SIGN_BG = (240, 236, 228)
SIGN_INK = (20, 20, 24)
CAP_BG = (8, 10, 14, 215)

STYLE_PROMO = (
    "Photorealistic construction-site promotional photograph. Bright daylight. "
    "High-gloss corporate ad aesthetic like over-the-counter medication commercials: "
    "every worker grinning with inappropriate cheer while doing difficult work. "
    "TUROV CONSTRUCTION LLC branding on vests or equipment. Cinematic shallow depth of field, "
    "35mm lens. No text overlays unless on in-world signage. No illustration. No anime. "
)

BG_PROMPTS: dict[str, str] = {
    "site_smile_wide": (
        "TUROV CONSTRUCTION LLC active excavation pit site panoramic. Orange compressor, "
        "nail pallets, chalk on cement. Workers too cheerful for the work."
    ),
    "stamper_suit_site": (
        "Rugged middle-aged man as Harry Stamper from Armageddon: grimy white asteroid-mining "
        "pressurized EVA suit with hoses and mission patches, hard hat over helmet, believes "
        "this is normal everyday work clothes. Earth construction site, drill rig behind him, "
        "clipboard, absurd pharma-ad grin."
    ),
    "stamper_bucket_lecture": (
        "Harry Stamper asteroid miner in white EVA suit pointing at orange bucket with exactly "
        "two loose nails, explaining to inspector, chalk tallies on cement, TUROV vest."
    ),
    "stamper_annotations": (
        "Harry Stamper in EVA suit writing ANNOTATIONS on clipboard at job site, coins in "
        "foreground, too cheerful, compressor hoses."
    ),
    "happy_nailgun": (
        "Happy Gilmore: 1990s hockey-golfer comedy protagonist energy, backward cap, loud shirt, "
        "connected nail gun and orange compressor, tossing one nail into bucket, manic ad-smile."
    ),
    "happy_chalk_snore": (
        "Happy Gilmore at construction site eyes closed fake snore on cement next to fresh chalk "
        "tally, nail gun in hand, compressor running, inappropriate blissful smile."
    ),
    "happy_rack_swap": (
        "Happy Gilmore holding two nail-gun magazine racks parallel counting sheaths, swapping "
        "order, huge pharmaceutical-ad grin, TUROV CONSTRUCTION site."
    ),
    "happy_coins_offer": (
        "Happy Gilmore offering penny and nickel in open palm to coworkers at site, coins visible, "
        "nail bucket and compressor, cheerful ad aesthetic."
    ),
    "winslade_inspection": (
        "Winslade from Undying Mercenaries: corporate mercenary safety administrator, hard hat, "
        "hi-vis vest with star-mercenary corp patches, tablet on lanyard, logging site observations, "
        "polite professional smile like a hemorrhoid relief commercial."
    ),
    "winslade_writing_two_nails": (
        "Winslade mercenary inspector writing on tablet while staring at bucket with two nails, "
        "Stamper-like figure blurred in white suit background, TUROV site."
    ),
    "winslade_chalk_coin": (
        "Winslade reading chalk iteration tally on cement, pointing at mark, inspector rig, "
        "compressor and nail racks visible."
    ),
    "vincent_coin_desk": (
        "Intense Vincent at site trailer whiteboard: truth coin.dat node diagram, file offsets, "
        "cc minus O zero compile line, not checking notes, knows it, TUROV mug."
    ),
    "vincent_site_knowing": (
        "Vincent in lab coat and hard hat at outdoor site explaining coin.secret twenty-five bytes, "
        "laptop showing coda, unbothered certainty, coworkers smile too happily."
    ),
    "rack_bucket_cycle": (
        "Close-up two nail-gun racks plastic sheaths, bucket with two nails, chalk mark, bleed hose."
    ),
    "bleed_line_gun": (
        "Happy Gilmore bleeding air from nail-gun hose eyes closed faux bliss, compressor humming."
    ),
    "coin_flip_spin": (
        "Copper penny and silver nickel mid-air spin above cement chalk marks, workers blurred "
        "cheering with pharma-ad joy, construction site daylight."
    ),
    "coin_on_cement": (
        "Coins heads-up on cement beside chalk tally iteration note, nail bucket, golden hour site."
    ),
    "yeshua_cosmic_carpenter": (
        "Carpenter in work clothes at TUROV site, normal human body hands and boots, but head is a "
        "cosmic cat face — deep space starfield and nebula forming a cat-head silhouette with glowing "
        "stellar eyes, reaching toward nail bucket, inappropriate cheerful smile in the cosmic cat face."
    ),
    "man_nails_request": (
        "Ordinary construction worker gesturing at bucket of loose nails while Winslade types on "
        "tablet and Happy Gilmore shrugs cheerfully, Stamper in EVA suit observes."
    ),
    "emmet_lego_foreman": (
        "LEGO Emmet style yellow construction foreman minifigure come to life at real job site, "
        "absurd optimism, real-scale workers in background looking bored, TUROV banner."
    ),
    "trio_compressor": (
        "Three-shot: Harry Stamper EVA suit, Happy Gilmore nail gun, Winslade mercenary inspector "
        "around orange air compressor, all inappropriately smiling like medication ad."
    ),
    "boston_bruins_happy": (
        "Happy Gilmore in Bruins jersey under construction vest, site still active, rejected-then-"
        "approved paperwork on clipboard, winslade-style inspector shrugging, pharma cheer."
    ),
    "operational_deficiency": (
        "Winslade filing operational deficiency on tablet, unsolicited nails request, bucket foreground, "
        "Stamper and Happy in frame, TUROV site."
    ),
}

SITE_MARKERS = (
    re.compile(r"construction site is active", re.I),
    re.compile(r"TUROV CONSTRUCTION", re.I),
    re.compile(r"Happy Gilmore is working", re.I),
)

TUROV_CUE_MARKER = re.compile(r"construction site is active", re.I)


def load_coda_lines() -> list[str]:
    raw = SRC.read_text(encoding="utf-8")
    m = re.search(r'^"""\s*\n(.*?)^"""', raw, re.M | re.S)
    if m:
        return [ln.rstrip() for ln in m.group(1).splitlines()]
    if CODA.exists():
        return CODA.read_text(encoding="utf-8").splitlines()
    return []


def load_turov_ascii() -> list[str]:
    raw = SRC.read_text(encoding="utf-8")
    m = re.search(r"```\s*\n(╔[\s\S]*?╚[^\n]*)\n```", raw)
    if not m:
        return []
    return [ln.rstrip("\n") for ln in m.group(1).splitlines()]


def spoken_step_num(text: str) -> int | None:
    m = re.search(
        r"step\s+(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)",
        text,
        re.I,
    )
    if not m:
        return None
    word = m.group(1).lower()
    names = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12,
    }
    if word.isdigit():
        return int(word)
    return names.get(word)


def guess_code_line(text: str, code_lines: list[str], hint: int) -> int:
    """Map spoken-code cue to a source line index."""
    t = text.strip()
    if not code_lines:
        return 0
    # puts string in spoken form
    pm = re.search(r'puts open-paren "(.*?)"', t)
    if pm:
        frag = pm.group(1).replace("double-arrow ", ">> ").replace("comma", ",")[:48]
        for i, ln in enumerate(code_lines):
            if frag and frag[:24] in ln:
                return i
    step = spoken_step_num(t)
    if step is not None:
        for i, ln in enumerate(code_lines):
            if re.search(rf"Step {step}\b|step {step}\b", ln, re.I):
                return i
    if "INITIALISERING" in t or "init open-paren" in t:
        for i, ln in enumerate(code_lines):
            if "static void init" in ln or "First run" in ln:
                return i
    if "HOVEDDEL" in t or "int main" in t:
        for i, ln in enumerate(code_lines):
            if "int main" in ln:
                return i
    if "close-brace" == t.replace(" ", ""):
        return min(hint + 1, len(code_lines) - 1)
    for token in ("PATH SEC", "PATH DAT", "rotate_address", "list_traverse", "execv"):
        if token.lower().replace(" ", "") in t.lower().replace(" ", "").replace("-", ""):
            for i, ln in enumerate(code_lines):
                if token.replace(" ", "_").lower() in ln.lower().replace(" ", "_") or token in ln:
                    return i
    qm = re.findall(r'"([^"]{8,60})"', t)
    for q in qm:
        qn = q.replace("percent-d", "%d").replace("percent-llu", "%llu")
        for i, ln in enumerate(code_lines):
            if q[:20] in ln or qn[:20] in ln:
                return i
    return min(max(hint, 0), len(code_lines) - 1)


def build_line_map(cues: list[dict], code_lines: list[str]) -> list[int]:
    site_i = site_phase_start(cues)
    lines: list[int] = []
    hint = 0
    for i, c in enumerate(cues):
        if i >= site_i or c["speaker"] != "The Narrator":
            lines.append(hint)
            continue
        tx = c.get("text") or ""
        if tx.startswith("star ") and "open-paren" not in tx and "indent" not in tx:
            # Danish summary / headers — stay near top or previous
            if "CODA" in tx or "coda.c" in tx:
                hint = 0
            lines.append(hint)
            continue
        hint = guess_code_line(tx, code_lines, hint)
        lines.append(hint)
    return lines


def site_phase_start(cues: list[dict]) -> int:
    for i, c in enumerate(cues):
        tx = c.get("text") or ""
        if TUROV_CUE_MARKER.search(tx):
            return i
        if c["speaker"] not in ("The Narrator",):
            return i
    return len(cues)


def turov_phase_end(cues: list[dict], start: int) -> int:
    """Show sign through early site narrator beats before dialogue."""
    for i in range(start, min(start + 14, len(cues))):
        if cues[i]["speaker"] != "The Narrator":
            return i
    return min(start + 12, len(cues))


KEYWORD_BG: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"Yeshua|Jesus|carpenter.*nails", re.I), "yeshua_cosmic_carpenter"),
    (re.compile(r"Emmet|LEGO|foreman.*awesome", re.I), "emmet_lego_foreman"),
    (re.compile(r"Bruins|hockey|game.*approved", re.I), "boston_bruins_happy"),
    (re.compile(r"operational deficiency|unplanned dependency|unsolicited request", re.I), "operational_deficiency"),
    (re.compile(r"ANNOTATIONS|annotation|blank section", re.I), "stamper_annotations"),
    (re.compile(r"penny|nickel|flipping|coin leaves|ringing|spinning", re.I), "coin_flip_spin"),
    (re.compile(r"Who wants which|offered them", re.I), "happy_coins_offer"),
    (re.compile(r"take those nails|need them to do my job", re.I), "man_nails_request"),
    (re.compile(r"rotation|thirty degrees|matrix multiplication|Step three", re.I), "stamper_bucket_lecture"),
    (re.compile(r"iteration|Elapsed|A-in-B|B-in-A", re.I), "winslade_chalk_coin"),
    (re.compile(r"two nails|Two cycles|accrues", re.I), "winslade_writing_two_nails"),
    (re.compile(r"astronaut|Stamper|suit|drills rocks|asteroid miner", re.I), "stamper_suit_site"),
    (re.compile(r"swap|racks parallel|sheath by sheath", re.I), "happy_rack_swap"),
    (re.compile(r"nail gun|compressor|Happy.Gilmore", re.I), "happy_nailgun"),
    (re.compile(r"snore|chalk mark", re.I), "happy_chalk_snore"),
    (re.compile(r"bleed the line|hose|pressure", re.I), "bleed_line_gun"),
    (re.compile(r"bucket.*nail|rack.*sheath", re.I), "rack_bucket_cycle"),
    (re.compile(r"Winslade|Carter|inspection|procedure|walk me through", re.I), "winslade_inspection"),
    (re.compile(r"Vincent|coin\.dat|coin\.secret|file offset|truth slash coda", re.I), "vincent_coin_desk"),
    (re.compile(r"running since before", re.I), "vincent_site_knowing"),
    (re.compile(r"heads\.|coin is on the flat|flat surface", re.I), "coin_on_cement"),
    (re.compile(r"construction site is active|introduce the people", re.I), "trio_compressor"),
]


def visual_for_cue(
    c: dict,
    i: int,
    cues: list[dict],
    line_map: list[int],
) -> tuple[str, int | None]:
    """Return (visual_id, code_scroll_line). code_scroll_line set only in code phase."""
    site0 = site_phase_start(cues)
    turov1 = turov_phase_end(cues, site0)
    tx = c.get("text") or ""
    sp = c["speaker"]

    if i < site0:
        return ("code", line_map[i] if i < len(line_map) else 0)

    if site0 <= i < turov1:
        return ("turov_sign_scene", None)

    bg = "site_smile_wide"
    for rx, name in KEYWORD_BG:
        if rx.search(tx) or (sp != "The Narrator" and rx.search(sp)):
            bg = name
            break
    if sp == "Vincent":
        bg = "vincent_coin_desk"
    elif sp in ("Winslade", "Carter"):
        bg = "winslade_inspection"
    elif sp == "Happy":
        bg = "happy_nailgun"
    elif sp == "Stamper":
        bg = "stamper_suit_site"
    return (bg, None)


# ── Audio ─────────────────────────────────────────────────────────────────────

def cmd_audio() -> None:
    import build_lisbeth_audio as lb

    lb.main = lb.main  # noqa: unused — invoke via subprocess for clean argv
    subprocess.run(
        [sys.executable, str(BASE / "tools" / "build_lisbeth_audio.py"), "--only", "09"],
        check=True,
        cwd=str(BASE),
    )


# ── Stills ────────────────────────────────────────────────────────────────────

def render_image(sid: str, prompt: str, dest: Path, *, force: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not force and dest.exists() and dest.stat().st_size > 8000:
        print(f"  [skip] {sid}")
        return
    import requests

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY for --render stills")
    payload = {
        "model": "gpt-image-1.5",
        "prompt": STYLE_PROMO + prompt,
        "size": "1536x1024",
        "quality": "high",
        "output_format": "png",
        "n": 1,
    }
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code}: {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid} ({dest.stat().st_size // 1024} KB)")


def draw_turov_sign_png(path: Path) -> None:
    import pygame

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    surf = pygame.Surface((W, H))
    surf.fill(SIGN_BG)
    font = pygame.font.SysFont("monospace", 13)
    lines = load_turov_ascii()
    if not lines:
        lines = ["TUROV CONSTRUCTION LLC", "ADVISORY SITE SAFETY ADVISORY"]
    y = 24
    for ln in lines:
        if len(ln) > 120:
            ln = ln[:117] + "..."
        surf.blit(font.render(ln, True, SIGN_INK), (32, y))
        y += 16
        if y > H - 80:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, path)
    print(f"  [ok] turov_sign.png ({path.stat().st_size // 1024} KB)")


def cmd_turov(render: bool = False, force: bool = False) -> None:
    sys.path.insert(0, str(BASE / "tools"))
    import compose_turov_sign as cts

    STILLS.mkdir(parents=True, exist_ok=True)
    blank = STILLS / "sign_blank_template.png"
    pit = STILLS / "site_pit_excavator.png"
    if render or force:
        if force or not blank.exists():
            print("── TUROV blank sign ──")
            cts.render_api(cts.BLANK_PROMPT, blank, size="1024x1536")
        if force or not pit.exists():
            print("── TUROV site pit ──")
            cts.render_api(cts.PIT_BG_PROMPT, pit, size="1536x1024")
    cts.compose(blank, pit, STILLS / "turov_sign_scene.png")


def cmd_stills(render: bool = False, force_promo: bool = False) -> None:
    STILLS.mkdir(parents=True, exist_ok=True)
    stamper = BASE / "video" / "stills" / "characters" / "stamper.png"
    if stamper.exists() and not (STILLS / "stamper_ref.png").exists():
        shutil.copy2(stamper, STILLS / "stamper_ref.png")
    draw_turov_sign_png(STILLS / "turov_sign.png")
    try:
        import compose_turov_sign as cts

        blank, pit = STILLS / "sign_blank_template.png", STILLS / "site_pit_excavator.png"
        if render:
            if not blank.exists():
                cts.render_api(cts.BLANK_PROMPT, blank, size="1024x1536")
            if not pit.exists():
                cts.render_api(cts.PIT_BG_PROMPT, pit, size="1536x1024")
        if blank.exists() and pit.exists():
            cts.compose(blank, pit, STILLS / "turov_sign_scene.png")
        elif render:
            cmd_turov(render=True)
    except Exception as exc:
        print(f"  [turov compose skip] {exc}")
    for sid, prompt in BG_PROMPTS.items():
        dest = STILLS / f"{sid}.png"
        if render:
            render_image(sid, prompt, dest, force=force_promo)
        else:
            print(f"  [dry] {sid}")


# ── Frames ────────────────────────────────────────────────────────────────────

CODE_VISIBLE = 22


def _load_bg(name: str):
    import pygame

    p = STILLS / f"{name}.png"
    if not p.exists() and name != "turov_sign":
        p = STILLS / "site_smile_wide.png"
    if not p.exists():
        return None
    img = pygame.image.load(str(p))
    return pygame.transform.smoothscale(img.convert(), (W, H))


def draw_code_panel(screen, code_lines: list[str], center_line: int, font_mono) -> None:
    import pygame

    panel = pygame.Surface((W - 48, H - 120), pygame.SRCALPHA)
    panel.fill((*CODE_BG, 245))
    screen.blit(panel, (24, 40))
    half = CODE_VISIBLE // 2
    start = max(0, center_line - half)
    end = min(len(code_lines), start + CODE_VISIBLE)
    start = max(0, end - CODE_VISIBLE)
    y = 52
    for i in range(start, end):
        ln = code_lines[i]
        if len(ln) > 108:
            ln = ln[:105] + "..."
        color = CODE_HI if i == center_line else CODE_FG
        if ln.strip().startswith("/*") or ln.strip().startswith("*"):
            color = CODE_DIM
        screen.blit(font_mono.render(f"{i+1:4d}  {ln}", True, color), (40, y))
        y += 26


def draw_frame(screen, cue: dict, vis: str, code_line: int | None, fonts, code_lines: list[str]) -> None:
    import pygame

    font, font_mono = fonts
    if vis == "code":
        screen.fill(CODE_BG)
        draw_code_panel(screen, code_lines, code_line or 0, font_mono)
    elif vis in ("turov_sign", "turov_sign_scene"):
        bg = _load_bg(vis)
        if bg is None:
            bg = _load_bg("turov_sign")
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill(SIGN_BG)
    else:
        bg = _load_bg(vis)
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((40, 44, 48))
            screen.blit(font.render(f"[ {vis} ]", True, (220, 220, 210)), (W // 2 - 120, H // 2))

    bar = pygame.Surface((W, 68), pygame.SRCALPHA)
    bar.fill(CAP_BG)
    screen.blit(bar, (0, H - 68))
    sp = cue.get("speaker", "")
    if sp == "Carter":
        sp = "Winslade"
    cap = (cue.get("text") or "")[:96]
    screen.blit(font.render(sp, True, (230, 220, 200)), (36, H - 58))
    screen.blit(font_mono.render(cap, True, (200, 198, 188)), (36, H - 32))


def load_cues() -> list[dict]:
    p = AUDIO / "cues.jsonl"
    if not p.exists():
        sys.exit(f"Missing {p} — run audio first")
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def cmd_frames() -> None:
    import pygame

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))
    screen = pygame.Surface((W, H))
    font = pygame.font.SysFont("serif", 20)
    font_mono = pygame.font.SysFont("monospace", 14)

    cues = load_cues()
    code_lines = load_coda_lines()
    line_map = build_line_map(cues, code_lines)
    STILLS.mkdir(parents=True, exist_ok=True)
    if not (STILLS / "turov_sign.png").exists():
        draw_turov_sign_png(STILLS / "turov_sign.png")

    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()

    seen: dict[tuple, str] = {}
    holds: list[tuple[str, float, float]] = []
    n = 0
    for i, c in enumerate(cues):
        vis, cl = visual_for_cue(c, i, cues, line_map)
        key = (vis, cl if vis == "code" else None, c["speaker"])
        if key not in seen:
            draw_frame(screen, c, vis, cl, (font, font_mono), code_lines)
            name = f"f{n:04d}.png"
            pygame.image.save(screen, FRAMES / name)
            seen[key] = name
            n += 1
            if n % 15 == 0:
                print(f"  unique {n}")
        rel = f"frames/{seen[key]}"
        start, end = float(c["start"]), float(c["end"])
        if holds and holds[-1][0] == rel:
            holds[-1] = (rel, holds[-1][1], end)
        else:
            holds.append((rel, start, end))

    timeline: list[tuple[str, float]] = []
    t = 0.0
    for rel, start, end in holds:
        dur = max(0.04, end - start)
        timeline.append((rel, dur))
        t += dur

    mp3 = AUDIO / "minus09.mp3"
    audio_dur = float(
        subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(mp3),
            ],
            capture_output=True,
            text=True,
        ).stdout.strip()
        or "0"
    )
    if audio_dur > 0 and timeline:
        drift = audio_dur - t
        name, dur = timeline[-1]
        timeline[-1] = (name, max(0.04, dur + drift))

    (OUT / "holds.json").write_text(
        json.dumps([{"file": rel, "duration": round(dur, 4)} for rel, dur in timeline], indent=1)
        + "\n"
    )
    concat = ["ffconcat version 1.0"]
    last = ""
    for rel, dur in timeline:
        concat.append(f"file '{rel}'")
        concat.append(f"duration {dur:.4f}")
        last = rel
    concat.append(f"file '{last}'")
    (OUT / "concat.txt").write_text("\n".join(concat) + "\n")
    print(
        f"Frames → {FRAMES} ({n} unique, {len(timeline)} holds, "
        f"{sum(d for _, d in timeline):.1f}s vs audio {audio_dur:.1f}s)"
    )


def cmd_assemble() -> None:
    mp3 = AUDIO / "minus09.mp3"
    if not mp3.exists():
        sys.exit("missing audio")
    concat = OUT / "concat.txt"
    if not concat.exists():
        sys.exit("missing frames — run frames")
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / "-09_coda_construction.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", "concat.txt",
            "-i", str(mp3),
            "-vf", "fps=1,format=yuv420p",
            "-c:v", "libx264", "-tune", "stillimage", "-crf", "20",
            "-g", "30", "-bf", "0",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(final),
        ],
        check=True,
        cwd=str(OUT),
    )
    print(f"Video → {final} ({final.stat().st_size // 1024 // 1024} MB)")


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "cmd",
        choices=["audio", "stills", "frames", "assemble", "all", "turov"],
    )
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--force", action="store_true", help="Regenerate TUROV PNG assets")
    ap.add_argument(
        "--force-promo",
        action="store_true",
        help="Re-render all promo stills even if files exist",
    )
    args = ap.parse_args()
    if args.cmd == "audio":
        cmd_audio()
    elif args.cmd == "turov":
        cmd_turov(render=args.render or args.force, force=args.force)
    elif args.cmd == "stills":
        cmd_stills(render=args.render, force_promo=args.force_promo)
    elif args.cmd == "frames":
        cmd_frames()
    elif args.cmd == "assemble":
        cmd_assemble()
    elif args.cmd == "all":
        cmd_audio()
        cmd_stills(render=args.render, force_promo=args.force_promo)
        if args.render:
            cmd_turov(render=True)
        cmd_frames()
        cmd_assemble()


if __name__ == "__main__":
    main()

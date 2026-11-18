#!/usr/bin/env python3
"""Build the standalone Page −07 film from its existing narration.

The visual register is the clean full-colour player art established by −08.
Goines stands in the room as the player figures stand at the table; exact
instrument diagrams carry the mechanism beside him.

    .venv/bin/python tools/build_minus07_video.py all
    .venv/bin/python tools/build_minus07_video.py frames
    .venv/bin/python tools/build_minus07_video.py assemble
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "phase2" / "-07.md"
OUT = BASE / "video" / "minus07"
FRAMES = OUT / "frames"
AUDIO_OUT = BASE / "audio" / "minus07"
BACKGROUNDS = BASE / "video" / "stills" / "layers" / "backgrounds"
PLAYER = OUT / "stills" / "players" / "goines_main.png"
BOOK_VIDEO = (
    BASE / "video" / "quarantine" / "book_mix" /
    "REALITY_USER_MANUAL_v0.0.2.mp4"
)
BOOK_CUES = BASE / "video" / "cues.jsonl"
GENERATED_PLAYER = Path(
    "/home/dylanmccapes/.cursor/projects/home-dylanmccapes-dev/assets/"
    "goines_player_main.jpg"
)

W, H = 1280, 720
FPS = 30
INK = (17, 19, 22)
BONE = (237, 229, 207)
AMBER = (220, 138, 42)
BLUE = (53, 105, 129)
RED = (157, 57, 42)

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size)


def ffprobe_dur(path: Path) -> float:
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


def narration() -> tuple[list[tuple[str, str]], list[dict]]:
    sys.path.insert(0, str(BASE / "tools"))
    import generate_phase2_audio as p2

    rows = p2.parse_07(SRC)
    source_cues = [
        json.loads(line)
        for line in BOOK_CUES.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("section") == "Page -07"
    ]
    if len(rows) != len(source_cues):
        raise SystemExit(
            f"Page −07 has {len(rows)} text segments but {len(source_cues)} book cues. "
            "The standalone film will not guess their alignment."
        )
    return rows, source_cues


def prepare_player() -> None:
    """Copy the generated player plate and flood-remove its white exterior."""
    if PLAYER.exists() and PLAYER.stat().st_size > 10_000:
        return
    if not GENERATED_PLAYER.exists():
        raise SystemExit(f"Missing generated Goines player art: {GENERATED_PLAYER}")

    raw = Image.open(GENERATED_PLAYER).convert("RGB")
    width, height = raw.size
    px = raw.load()
    exterior = Image.new("L", raw.size, 255)
    mask_px = exterior.load()
    queue: deque[tuple[int, int]] = deque()

    def is_background(x: int, y: int) -> bool:
        r, g, b = px[x, y]
        return min(r, g, b) >= 239 and max(r, g, b) - min(r, g, b) <= 12

    for x in range(width):
        if is_background(x, 0):
            queue.append((x, 0))
        if is_background(x, height - 1):
            queue.append((x, height - 1))
    for y in range(height):
        if is_background(0, y):
            queue.append((0, y))
        if is_background(width - 1, y):
            queue.append((width - 1, y))

    seen: set[tuple[int, int]] = set()
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or not is_background(x, y):
            continue
        seen.add((x, y))
        mask_px[x, y] = 0
        if x:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))

    # A one-pixel soft edge avoids a white contour without erasing the smock.
    exterior = exterior.filter(ImageFilter.GaussianBlur(0.65))
    rgba = raw.convert("RGBA")
    rgba.putalpha(exterior)
    PLAYER.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(PLAYER)


def cover_background(name: str) -> Image.Image:
    path = BACKGROUNDS / f"{name}.png"
    if not path.exists():
        path = BACKGROUNDS / "goines_room.png"
    raw = Image.open(path).convert("RGB")
    scale = max(W / raw.width, H / raw.height)
    resized = raw.resize(
        (round(raw.width * scale), round(raw.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def panel(draw: ImageDraw.ImageDraw, title: str, *, side: str = "left") -> tuple[int, int, int, int]:
    x0 = 48 if side == "left" else 736
    x1 = x0 + 496
    y0, y1 = 52, 666
    draw.rounded_rectangle(
        (x0, y0, x1, y1),
        radius=18,
        fill=(15, 17, 20, 238),
        outline=(221, 200, 158, 235),
        width=3,
    )
    draw.text((x0 + 28, y0 + 24), title.upper(), font=font(24, bold=True), fill=BONE)
    draw.line((x0 + 28, y0 + 66, x1 - 28, y0 + 66), fill=AMBER, width=3)
    return x0, y0, x1, y1


def draw_battery(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    cx = (x0 + x1) // 2
    top = y0 + 108
    labels = [("Cu", BLUE), ("GYPSUM + RAIN", BONE), ("Zn", AMBER)]
    for cell in range(4):
        cy = top + cell * 105
        draw.rounded_rectangle((cx - 168, cy, cx + 168, cy + 72), 8, outline=BONE, width=2)
        widths = [64, 190, 64]
        x = cx - 159
        for (label, colour), width in zip(labels, widths):
            draw.rectangle((x, cy + 9, x + width, cy + 63), fill=colour)
            tx = x + width // 2
            draw.text((tx, cy + 36), label, font=font(15, bold=True), fill=INK, anchor="mm")
            x += width
        if cell < 3:
            draw.line((cx + 168, cy + 36, cx + 190, cy + 36, cx + 190, cy + 105),
                      fill=AMBER, width=3)
    draw.text((cx, top + 448), "four cells · series · ≈ 4 V", font=font(20, mono=True),
              fill=BONE, anchor="mm")


def draw_barcode(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    widths = [8, 21, 8, 8, 21, 21, 8, 21, 8, 21, 8, 8, 21, 8]
    total = sum(widths) + 8 * (len(widths) - 1)
    x = (x0 + x1 - total) // 2
    top = y0 + 126
    for width in widths:
        draw.rectangle((x, top, x + width, top + 235), fill=BONE)
        x += width + 8
    draw.text(((x0 + x1) // 2, top + 282), "wide  →  lower resistance",
              font=font(20, mono=True), fill=AMBER, anchor="mm")
    draw.text(((x0 + x1) // 2, top + 325), "narrow →  higher resistance",
              font=font(20, mono=True), fill=BLUE, anchor="mm")
    draw.text(((x0 + x1) // 2, top + 410), "GEOMETRY BECOMES SIGNAL",
              font=font(19, bold=True), fill=BONE, anchor="mm")


def resistor(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int]) -> None:
    ax, ay = a
    bx, by = b
    points = []
    steps = 9
    for i in range(steps + 1):
        t = i / steps
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t
        if 1 < i < steps - 1:
            off = 10 if i % 2 else -10
            dx, dy = bx - ax, by - ay
            mag = max(1.0, (dx * dx + dy * dy) ** 0.5)
            x += -dy / mag * off
            y += dx / mag * off
        points.append((round(x), round(y)))
    draw.line(points, fill=BONE, width=4)


def draw_bridge(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    cx = (x0 + x1) // 2
    top, left, right, bottom = (cx, y0 + 125), (cx - 165, y0 + 295), (cx + 165, y0 + 295), (cx, y0 + 465)
    resistor(draw, top, left)
    resistor(draw, top, right)
    resistor(draw, left, bottom)
    resistor(draw, right, bottom)
    draw.line((left, right), fill=AMBER, width=4)
    draw.ellipse((cx - 42, y0 + 253, cx + 42, y0 + 337), outline=AMBER, width=4)
    draw.text((cx, y0 + 295), "G", font=font(30, bold=True), fill=AMBER, anchor="mm")
    for p in (top, left, right, bottom):
        draw.ellipse((p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6), fill=BONE)
    draw.text((cx, y0 + 530), "DIFFERENCE, NOT ABSOLUTE",
              font=font(19, bold=True), fill=BONE, anchor="mm")


def draw_galvanometer(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    cx = (x0 + x1) // 2
    for radius in range(155, 65, -12):
        draw.ellipse((cx - radius, y0 + 125, cx + radius, y0 + 125 + radius * 2),
                     outline=BLUE, width=3)
    draw.ellipse((cx - 62, y0 + 218, cx + 62, y0 + 342), fill=INK, outline=BONE, width=3)
    draw.line((cx, y0 + 280, cx + 48, y0 + 222), fill=AMBER, width=7)
    draw.ellipse((cx - 8, y0 + 272, cx + 8, y0 + 288), fill=AMBER)
    draw.text((cx, y0 + 500), "LEFT  ·  NULL  ·  RIGHT",
              font=font(19, mono=True), fill=BONE, anchor="mm")
    draw.text((cx, y0 + 548), "five degrees is enough",
              font=font(18), fill=AMBER, anchor="mm")


def draw_decode(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    cx = (x0 + x1) // 2
    draw_barcode(draw, (x0, y0 - 35, x1, y0 + 380))
    draw.rectangle((x0 + 45, y0 + 430, x1 - 45, y0 + 552), outline=AMBER, width=3)
    draw.text((cx, y0 + 470), "· — · · — — · —", font=font(25, mono=True),
              fill=BONE, anchor="mm")
    draw.text((cx, y0 + 522), "CODE 128 · HAND TRANSCRIPTION", font=font(16, bold=True),
              fill=AMBER, anchor="mm")


def draw_classification(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    cx = (x0 + x1) // 2
    draw.text((cx, y0 + 155), "PATIENT RECORD", font=font(22, mono=True),
              fill=(150, 156, 158), anchor="mm")
    draw.rectangle((x0 + 48, y0 + 205, x1 - 48, y0 + 390), outline=RED, width=4)
    draw.text((cx, y0 + 255), "INVOLUNTARY", font=font(27, bold=True), fill=BONE, anchor="mm")
    draw.text((cx, y0 + 305), "COMMITMENT", font=font(27, bold=True), fill=BONE, anchor="mm")
    draw.text((cx, y0 + 365), "EPISTEMIC DISRUPTION", font=font(20, mono=True),
              fill=RED, anchor="mm")
    draw.text((cx, y0 + 485), "THE REFERENCE IS NOT SHOWN",
              font=font(18, bold=True), fill=AMBER, anchor="mm")


def draw_refusal(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    cx = (x0 + x1) // 2
    draw.text((cx, y0 + 180), "ACHILLES", font=font(46, bold=True), fill=BONE, anchor="mm")
    draw.line((x0 + 95, y0 + 230, x1 - 95, y0 + 230), fill=AMBER, width=4)
    draw.text((cx, y0 + 310), "THE REFUSAL", font=font(31, bold=True), fill=AMBER, anchor="mm")
    draw.text((cx, y0 + 375), "WAS HIS AGENCY", font=font(31, bold=True), fill=AMBER, anchor="mm")
    draw.text((cx, y0 + 485), "potentially or simply not wrong",
              font=font(17), fill=BONE, anchor="mm")


def draw_derivation(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, _ = box
    lines = [
        "V_G = V_S [ R₂/(R₁+R₂)",
        "            − Rₓ/(R₃+Rₓ) ]",
        "",
        "V_G = 0",
        "",
        "R₁ / R₂ = R₃ / Rₓ",
    ]
    y = y0 + 145
    for line in lines:
        draw.text((x0 + 42, y), line, font=font(23, mono=True),
                  fill=AMBER if "=" in line and "0" in line else BONE)
        y += 57
    draw.text(((x0 + x1) // 2, y0 + 545), "ON RECORD SOMEWHERE",
              font=font(18, bold=True), fill=AMBER, anchor="mm")


def visual_for(text: str, index: int) -> tuple[str, str | None, str]:
    lower = text.lower()
    if index == 0:
        return "goines_room", None, "right"
    if "drip" in lower or "cheekbone" in lower:
        return "goines_cell_drip", None, "right"
    if "floor sloped" in lower or "drain" in lower:
        return "goines_cell_drain_slope", None, "right"
    if "anklet" in lower or "barcode" in lower and index < 13:
        return "goines_cell_barcode", "barcode", "right"
    if "breaker box" in lower or "electrodes" in lower:
        return "goines_cell_breaker", "battery", "right"
    if "battery" in lower or "gypcrete" in lower or "zinc-copper" in lower:
        return "goines_cell_battery", "battery", "right"
    if "conductive" in lower or "adhesive" in lower or "bic ink" in lower:
        return "goines_cell_barcode", "barcode", "right"
    if "wheatstone" in lower or "four resistors" in lower or "fourth leg" in lower:
        return "goines_room", "bridge", "right"
    if "galvanometer" in lower or "lightbulb" in lower or "solenoid" in lower or "needle deflected" in lower:
        return "goines_room", "galvanometer", "right"
    if "code 128" in lower or "dashes and dots" in lower or "began to read" in lower:
        return "goines_room", "decode", "right"
    if "classification" in lower or "epistemic disruption" in lower or "categorized" in lower:
        return "goines_room_night", "classification", "right"
    if "achilles" in lower or "odd thought" in lower or "refusal" in lower:
        return "goines_room_night", "refusal", "right"
    if "derivation" in lower or "picked up the pen" in lower or "on record" in lower:
        return "goines_cell_wall_write", "derivation", "right"
    if "dark again" in lower or "slept" in lower or "rain did not stop" in lower:
        return "goines_room_night", None, "left"
    return ("goines_room_night" if index > 35 else "goines_room", None, "left")


def title_frame(dest: Path) -> None:
    image = cover_background("goines_room_night").convert("RGBA")
    shade = Image.new("RGBA", image.size, (0, 0, 0, 118))
    image.alpha_composite(shade)
    draw = ImageDraw.Draw(image)
    draw.text((W // 2, 280), "PAGE −07", font=font(30, bold=True), fill=AMBER, anchor="mm")
    draw.text((W // 2, 350), "GOINES, JEFFERY", font=font(48, bold=True), fill=BONE, anchor="mm")
    draw.text((W // 2, 410), "the reference leg", font=font(20), fill=(185, 181, 170), anchor="mm")
    image.convert("RGB").save(dest, quality=94)


def frame_for(text: str, index: int, dest: Path) -> None:
    background_name, diagram, sprite_side = visual_for(text, index)
    image = cover_background(background_name).convert("RGBA")
    image.alpha_composite(Image.new("RGBA", image.size, (5, 7, 8, 38)))

    if diagram:
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        box = panel(draw, {
            "battery": "pore-solution battery",
            "barcode": "resistive map",
            "bridge": "Wheatstone bridge",
            "galvanometer": "moving-iron readout",
            "decode": "line by line",
            "classification": "last field",
            "refusal": "an available act",
            "derivation": "from first principles",
        }[diagram], side="left")
        {
            "battery": draw_battery,
            "barcode": draw_barcode,
            "bridge": draw_bridge,
            "galvanometer": draw_galvanometer,
            "decode": draw_decode,
            "classification": draw_classification,
            "refusal": draw_refusal,
            "derivation": draw_derivation,
        }[diagram](draw, box)
        image.alpha_composite(overlay)
        sprite_side = "right"

    sprite = Image.open(PLAYER).convert("RGBA")
    target_h = 645
    target_w = round(sprite.width * target_h / sprite.height)
    sprite = sprite.resize((target_w, target_h), Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_sprite = Image.new("RGBA", sprite.size, (0, 0, 0, 0))
    shadow_sprite.putalpha(sprite.getchannel("A").filter(ImageFilter.GaussianBlur(12)))
    x = W - target_w - 8 if sprite_side == "right" else 20
    y = H - target_h + 8
    shadow.alpha_composite(shadow_sprite, (x + 13, y + 10))
    image.alpha_composite(shadow)
    image.alpha_composite(sprite, (x, y))

    # Small page marker, never a subtitle.
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1130, 26, 1248, 68), 12, fill=(12, 14, 16, 210),
                           outline=(220, 138, 42, 210), width=2)
    draw.text((1189, 47), "−07", font=font(20, bold=True), fill=BONE, anchor="mm")
    image.convert("RGB").save(dest, quality=93)


def build_frames() -> list[dict]:
    prepare_player()
    rows, source_cues = narration()
    FRAMES.mkdir(parents=True, exist_ok=True)
    cues: list[dict] = []
    now = 0.0
    for index, ((_, text), source_cue) in enumerate(zip(rows, source_cues)):
        duration = float(source_cue["end"]) - float(source_cue["start"])
        if duration <= 0:
            raise SystemExit(f"Invalid source cue at Page −07 segment {index}")
        dest = FRAMES / f"{index:04d}.jpg"
        if index == 0:
            title_frame(dest)
        else:
            frame_for(text, index, dest)
        cues.append({
            "start": now,
            "end": now + duration,
            "dur": duration,
            "speaker": "Goines",
            "text": text,
            "frame": dest.name,
        })
        now += duration

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cues.jsonl").write_text(
        "".join(json.dumps(cue, ensure_ascii=False) + "\n" for cue in cues),
        encoding="utf-8",
    )
    # The title frame is also the listen-desk poster.
    Image.open(FRAMES / "0000.jpg").save(OUT / "poster.jpg", quality=94)
    print(f"frames {len(cues)} · duration {now:.3f}s")
    return cues


def build_audio() -> Path:
    _, source_cues = narration()
    AUDIO_OUT.mkdir(parents=True, exist_ok=True)
    start = float(source_cues[0]["start"])
    end = float(source_cues[-1]["end"])
    duration = end - start
    target = AUDIO_OUT / "minus07.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(BOOK_VIDEO),
            "-ss", f"{start:.6f}", "-t", f"{duration:.6f}", "-vn",
            "-c:a", "libmp3lame", "-q:a", "2", str(target),
        ],
        check=True,
    )
    return target


def assemble() -> Path:
    cues = build_frames()
    audio = build_audio()
    visuals = OUT / "visuals.txt"
    lines: list[str] = []
    for cue in cues:
        path = (FRAMES / cue["frame"]).resolve()
        lines.extend((f"file '{path}'", f"duration {cue['dur']:.6f}"))
    lines.append(f"file '{(FRAMES / cues[-1]['frame']).resolve()}'")
    visuals.write_text("\n".join(lines) + "\n", encoding="utf-8")

    target = OUT / "-07_goines_jeffery.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(visuals),
            "-i", str(audio),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest",
            str(target),
        ],
        check=True,
    )
    print(f"video {target} · {ffprobe_dur(target):.3f}s")
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("frames", "audio", "assemble", "all"), nargs="?", default="all")
    args = parser.parse_args()
    if args.command == "frames":
        build_frames()
    elif args.command == "audio":
        build_audio()
    else:
        assemble()


if __name__ == "__main__":
    main()

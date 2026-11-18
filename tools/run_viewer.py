#!/usr/bin/env python3
"""pygame viewer: plays −08 audio synchronized with scene images.

Layout (default 1280×720):
  - Background: full screen (scene image, crossfades on setting change)
  - Portrait: 280×280, lower-left, fades in when character speaks
  - Subtitle: bottom strip — speaker name + beginning of line
  - Roll flash: brief white pulse when a roll lands

Controls:
  SPACE     pause / resume
  ← / →    seek −30s / +30s
  F         fullscreen toggle
  ESC       quit

Usage:
  .venv/bin/python tools/run_viewer.py
  .venv/bin/python tools/run_viewer.py --no-audio   # images only, auto-advance
  .venv/bin/python tools/run_viewer.py --width 1920 --height 1080
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Headless guard — allow running where DISPLAY is not set
if os.environ.get("SDL_VIDEODRIVER") == "dummy":
    pass  # test mode

try:
    import pygame
except ImportError:
    sys.exit("pygame not installed: .venv/bin/pip install pygame")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

BASE = Path(__file__).resolve().parent.parent
AUDIO_PATH = BASE / "audio" / "minus08" / "minus08.mp3"
CUES_PATH = BASE / "audio" / "minus08" / "cues.jsonl"
IMG_DIR = BASE / "images" / "minus08"
SCENES_PATH = IMG_DIR / "scenes.jsonl"
PORTRAITS_PATH = IMG_DIR / "portraits.jsonl"

# ── Colours ───────────────────────────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK = (10, 8, 6)
SUBTITLE_BG = (0, 0, 0, 160)  # RGBA
PORTRAIT_SHADOW = (0, 0, 0, 100)

CROSSFADE_MS = 1500       # background crossfade duration
PORTRAIT_FADE_IN_MS = 300
PORTRAIT_FADE_OUT_MS = 600
ROLL_FLASH_MS = 120       # white pulse duration
ROLL_FLASH_ALPHA = 70     # 0–255

NARRATOR_SPEAKERS = {"The Narrator", "The NarratorAf", "Terminal"}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def load_surface(path: Path | str, target_size: tuple[int, int] | None = None) -> pygame.Surface | None:
    p = Path(path) if isinstance(path, str) else path
    if not p.exists():
        return None
    try:
        surf = pygame.image.load(str(p)).convert()
        if target_size:
            surf = pygame.transform.smoothscale(surf, target_size)
        return surf
    except Exception:
        return None


def placeholder(size: tuple[int, int], color: tuple[int, int, int] = (30, 25, 20)) -> pygame.Surface:
    s = pygame.Surface(size)
    s.fill(color)
    return s


def lerp_alpha(a: float, b: float, t: float) -> float:
    return a + (b - a) * max(0.0, min(1.0, t))


class ImageCache:
    """Lazy-load and cache pygame Surfaces by path."""
    def __init__(self):
        self._cache: dict[str, pygame.Surface | None] = {}

    def get(self, path: str | None, size: tuple[int, int]) -> pygame.Surface:
        if not path:
            return placeholder(size)
        if path not in self._cache:
            self._cache[path] = load_surface(path, size)
        return self._cache[path] or placeholder(size)


class Viewer:
    def __init__(self, width: int, height: int, no_audio: bool):
        self.W = width
        self.H = height
        self.no_audio = no_audio

        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.display.set_caption("REALITY USER MANUAL — page −08")

        flags = 0
        self.screen = pygame.display.set_mode((self.W, self.H), flags)
        self.clock = pygame.time.Clock()
        self.cache = ImageCache()
        self.fullscreen = False
        self.paused = False

        # Subtitle font
        pygame.font.init()
        self.font_name = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_line = pygame.font.SysFont("monospace", 14)

        # Portrait dimensions
        self.PORT_SIZE = (int(self.H * 0.28), int(self.H * 0.28))
        self.PORT_X = 20
        self.PORT_Y = self.H - self.PORT_SIZE[1] - 20

        # Subtitle strip
        self.SUB_H = int(self.H * 0.12)
        self.sub_rect = pygame.Rect(0, self.H - self.SUB_H, self.W, self.SUB_H)

        # Load data
        self.cues = load_jsonl(CUES_PATH)
        self.scenes = load_jsonl(SCENES_PATH)
        self.portraits = {p["key"]: p for p in load_jsonl(PORTRAITS_PATH)}

        # Playback state
        self.pos_ms = 0.0
        self.audio_loaded = False
        self.audio_started = False
        self.start_wall = 0.0
        self.pause_wall = 0.0
        self.seek_offset_ms = 0.0

        # Scene state
        self.current_scene_idx = -1
        self.prev_bg: pygame.Surface | None = None
        self.curr_bg: pygame.Surface | None = None
        self.crossfade_start_ms: float | None = None  # wall-clock ms

        # Portrait state
        self.portrait_char: str | None = None
        self.portrait_surf: pygame.Surface | None = None
        self.portrait_alpha = 0.0   # 0.0–255.0
        self.portrait_target = 0.0

        # Roll flash
        self.roll_flash_end_ms: float | None = None
        self.last_cue_idx = -1

        # Current cue
        self.current_cue: dict | None = None

        # Load audio
        if not no_audio and AUDIO_PATH.exists():
            try:
                pygame.mixer.music.load(str(AUDIO_PATH))
                self.audio_loaded = True
            except Exception as e:
                print(f"[WARN] Could not load audio: {e}")

    def get_audio_pos_ms(self) -> float:
        if self.no_audio or not self.audio_started:
            return self.pos_ms
        if self.paused:
            return self.pos_ms
        raw = pygame.mixer.music.get_pos()  # ms since last play(), or -1
        if raw < 0:
            return self.pos_ms
        return raw + self.seek_offset_ms

    def start(self):
        if self.audio_loaded and not self.audio_started:
            pygame.mixer.music.play()
            self.audio_started = True
            self.start_wall = time.monotonic() * 1000

    def seek(self, delta_ms: float):
        if not self.audio_loaded:
            self.pos_ms = max(0, self.pos_ms + delta_ms)
            return
        new_pos = max(0, self.get_audio_pos_ms() + delta_ms)
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=new_pos / 1000.0)
        self.seek_offset_ms = new_pos
        self.pos_ms = new_pos
        if self.paused:
            pygame.mixer.music.pause()

    def toggle_pause(self):
        if not self.audio_loaded:
            self.paused = not self.paused
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.pause()
            self.pos_ms = self.get_audio_pos_ms()
            self.paused = True

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w, info.current_h), pygame.FULLSCREEN
            )
            self.W, self.H = info.current_w, info.current_h
        else:
            self.screen = pygame.display.set_mode((1280, 720))
            self.W, self.H = 1280, 720
        self._update_layout()

    def _update_layout(self):
        self.PORT_SIZE = (int(self.H * 0.28), int(self.H * 0.28))
        self.PORT_Y = self.H - self.PORT_SIZE[1] - 20
        self.SUB_H = int(self.H * 0.12)
        self.sub_rect = pygame.Rect(0, self.H - self.SUB_H, self.W, self.SUB_H)
        self.curr_bg = None  # force re-scale on next frame

    def find_scene(self, pos_ms: float) -> int:
        for i, s in enumerate(self.scenes):
            if s["start_ms"] <= pos_ms < s["end_ms"]:
                return i
        if self.scenes and pos_ms >= self.scenes[-1]["start_ms"]:
            return len(self.scenes) - 1
        return 0

    def find_cue(self, pos_ms: float) -> dict | None:
        for c in self.cues:
            if c["start"] * 1000 <= pos_ms < c["end"] * 1000:
                return c
        return None

    def _load_bg(self, scene_idx: int) -> pygame.Surface:
        if 0 <= scene_idx < len(self.scenes):
            path = BASE / self.scenes[scene_idx]["bg_path"]
            return self.cache.get(str(path), (self.W, self.H))
        return placeholder((self.W, self.H))

    def _load_portrait(self, char_key: str | None) -> pygame.Surface | None:
        if not char_key or char_key not in self.portraits:
            return None
        path = BASE / self.portraits[char_key]["path"]
        return self.cache.get(str(path), self.PORT_SIZE)

    def draw_subtitle(self, cue: dict | None):
        if not cue:
            return
        speaker = cue["speaker"]
        text = cue["text"]

        # Semi-transparent subtitle bar
        sub_surf = pygame.Surface((self.W, self.SUB_H), pygame.SRCALPHA)
        sub_surf.fill(SUBTITLE_BG)
        self.screen.blit(sub_surf, self.sub_rect.topleft)

        if speaker not in NARRATOR_SPEAKERS:
            name_surf = self.font_name.render(speaker.upper(), True, (220, 180, 100))
            self.screen.blit(name_surf, (self.sub_rect.x + 12, self.sub_rect.y + 6))
            y_text = self.sub_rect.y + 28
        else:
            y_text = self.sub_rect.y + 10

        # Wrap text to width
        words = text.split()
        line = ""
        y = y_text
        max_w = self.W - 24
        for word in words:
            test = (line + " " + word).strip()
            tw = self.font_line.size(test)[0]
            if tw > max_w and line:
                surf = self.font_line.render(line, True, (230, 230, 220))
                self.screen.blit(surf, (12, y))
                y += 18
                if y > self.sub_rect.bottom - 6:
                    break
                line = word
            else:
                line = test
        if line:
            surf = self.font_line.render(line, True, (230, 230, 220))
            self.screen.blit(surf, (12, y))

    def run(self):
        self.start()
        wall_ms = lambda: time.monotonic() * 1000

        # No-audio mode: advance at a fixed rate
        no_audio_speed = 1.0
        no_audio_t = wall_ms()

        running = True
        while running:
            dt = self.clock.tick(60)

            # Events
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key == pygame.K_SPACE:
                        self.toggle_pause()
                    elif ev.key == pygame.K_RIGHT:
                        self.seek(30_000)
                    elif ev.key == pygame.K_LEFT:
                        self.seek(-30_000)
                    elif ev.key == pygame.K_f:
                        self.toggle_fullscreen()

            # Update position
            if self.no_audio:
                if not self.paused:
                    now = wall_ms()
                    self.pos_ms += (now - no_audio_t) * no_audio_speed
                    no_audio_t = now
                else:
                    no_audio_t = wall_ms()
            else:
                self.pos_ms = self.get_audio_pos_ms()

            now_ms = wall_ms()

            # ── Scene update ─────────────────────────────────────────────────
            new_scene_idx = self.find_scene(self.pos_ms)
            if new_scene_idx != self.current_scene_idx:
                self.prev_bg = self.curr_bg or self._load_bg(self.current_scene_idx)
                self.curr_bg = self._load_bg(new_scene_idx)
                self.crossfade_start_ms = now_ms
                self.current_scene_idx = new_scene_idx

            # Ensure curr_bg is loaded (initial frame)
            if self.curr_bg is None:
                self.curr_bg = self._load_bg(self.current_scene_idx)

            # ── Current cue ──────────────────────────────────────────────────
            cue = self.find_cue(self.pos_ms)
            self.current_cue = cue

            # Portrait target — use table-room form when at the table
            if cue and cue["speaker"] not in NARRATOR_SPEAKERS:
                from scene_tracker import SPEAKER_CHAR, SPEAKER_CHAR_TABLE, TABLE_SETTINGS
                current_setting = (
                    self.scenes[self.current_scene_idx]["setting"]
                    if 0 <= self.current_scene_idx < len(self.scenes)
                    else ""
                )
                char_map = SPEAKER_CHAR_TABLE if current_setting in TABLE_SETTINGS else SPEAKER_CHAR
                new_char = char_map.get(cue["speaker"])
            else:
                new_char = None

            if new_char != self.portrait_char:
                if new_char:
                    self.portrait_char = new_char
                    self.portrait_surf = self._load_portrait(new_char)
                    self.portrait_target = 255.0
                else:
                    self.portrait_target = 0.0
                    if self.portrait_alpha < 5:
                        self.portrait_char = None

            # ── Roll flash ───────────────────────────────────────────────────
            if cue and "roll is" in cue.get("text", "").lower():
                cue_id = cue.get("i", -1)
                if cue_id != self.last_cue_idx:
                    self.roll_flash_end_ms = now_ms + ROLL_FLASH_MS
                    self.last_cue_idx = cue_id

            # ── Draw ─────────────────────────────────────────────────────────
            self.screen.fill(DARK)

            # Background (with crossfade)
            if self.crossfade_start_ms is not None and self.prev_bg is not None:
                elapsed = now_ms - self.crossfade_start_ms
                t = min(1.0, elapsed / CROSSFADE_MS)
                prev = pygame.transform.smoothscale(self.prev_bg, (self.W, self.H))
                curr = pygame.transform.smoothscale(self.curr_bg, (self.W, self.H))
                prev.set_alpha(int(255 * (1.0 - t)))
                self.screen.blit(prev, (0, 0))
                curr.set_alpha(int(255 * t))
                self.screen.blit(curr, (0, 0))
                if t >= 1.0:
                    self.crossfade_start_ms = None
                    self.prev_bg = None
            else:
                bg = pygame.transform.smoothscale(self.curr_bg, (self.W, self.H))
                self.screen.blit(bg, (0, 0))

            # Portrait fade
            speed = PORTRAIT_FADE_IN_MS if self.portrait_target > self.portrait_alpha else PORTRAIT_FADE_OUT_MS
            step = 255.0 * (dt / speed)
            if self.portrait_target > self.portrait_alpha:
                self.portrait_alpha = min(255.0, self.portrait_alpha + step)
            elif self.portrait_target < self.portrait_alpha:
                self.portrait_alpha = max(0.0, self.portrait_alpha - step)

            if self.portrait_alpha > 5 and self.portrait_surf:
                # Shadow behind portrait
                shadow = pygame.Surface(self.PORT_SIZE, pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 80))
                shadow_rect = pygame.Rect(self.PORT_X + 4, self.PORT_Y + 4, *self.PORT_SIZE)
                self.screen.blit(shadow, shadow_rect.topleft)

                port = self.portrait_surf.copy()
                port = pygame.transform.smoothscale(port, self.PORT_SIZE)
                port.set_alpha(int(self.portrait_alpha))
                self.screen.blit(port, (self.PORT_X, self.PORT_Y))

            # Roll flash overlay
            if self.roll_flash_end_ms and now_ms < self.roll_flash_end_ms:
                t = 1.0 - (now_ms - (self.roll_flash_end_ms - ROLL_FLASH_MS)) / ROLL_FLASH_MS
                flash = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
                flash.fill((255, 255, 255, int(ROLL_FLASH_ALPHA * t)))
                self.screen.blit(flash, (0, 0))

            # Subtitles
            self.draw_subtitle(cue)

            # Pause indicator
            if self.paused:
                paused_surf = self.font_name.render("⏸ PAUSED", True, (200, 200, 100))
                self.screen.blit(paused_surf, (self.W // 2 - 40, 20))

            pygame.display.flip()

        pygame.quit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    args = ap.parse_args()

    if not SCENES_PATH.exists():
        sys.exit("No scenes.jsonl found. Run: .venv/bin/python tools/scene_tracker.py first.")

    # Add tools to path for SPEAKER_CHAR import
    sys.path.insert(0, str(BASE / "tools"))

    viewer = Viewer(args.width, args.height, args.no_audio)
    viewer.run()


if __name__ == "__main__":
    main()

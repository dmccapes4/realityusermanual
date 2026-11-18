#!/usr/bin/env python3
"""Blueprint-table derivations and Ross citation papers for page −14 (07k).

Pygame, headless. The stills are the exact objects on the table:
Sheldon's ticks / χ / softmax / 1/t / t½, Ted's rectangles and deed line,
Ross's four papers with the real citation and abstract.

  .venv/bin/python tools/triad_blueprint.py all
  .venv/bin/python tools/triad_blueprint.py stills
  .venv/bin/python tools/triad_blueprint.py anim
  .venv/bin/python tools/triad_blueprint.py papers
"""
from __future__ import annotations

import argparse
import math
import os
import textwrap
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "video" / "minus14" / "blueprint"
ANIM = OUT / "anim"
PAPERS = OUT / "papers"

W, H = 1536, 1024
PAPER_W, PAPER_H = 1280, 720

NAVY = (16, 38, 68)
GRID = (26, 58, 92)
LINE = (38, 78, 118)
INK = (226, 232, 214)
PENCIL = (210, 198, 148)
GOLD = (232, 188, 86)
RED = (196, 92, 86)
PALE = (168, 196, 186)
BRASS = (176, 148, 72)
STEEL = (140, 156, 168)
WOOD = (42, 64, 58)
USB = (28, 28, 30)

CREAM = (244, 236, 214)
INK_K = (28, 22, 18)
RULE = (170, 40, 40)
MUTED = (90, 78, 64)
HAND = (176, 142, 112)

FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_B = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FONT_S = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
FONT_SI = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf")
FONT_SB = Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")


def _font(path: Path, size: int) -> pygame.font.Font:
    if path.exists():
        return pygame.font.Font(str(path), size)
    return pygame.font.SysFont("serif", size)


def blit_text(surf, font, text, xy, color=INK, anchor="tl"):
    img = font.render(text, True, color)
    r = img.get_rect()
    x, y = xy
    if anchor == "c":
        r.center = (x, y)
    elif anchor == "tr":
        r.topright = (x, y)
    elif anchor == "bl":
        r.bottomleft = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)
    return r


def write_chars(surf, font, text, xy, color, progress: float):
    n = max(0, min(len(text), int(round(len(text) * progress))))
    if n:
        blit_text(surf, font, text[:n], xy, color)


def table(size=(W, H)) -> pygame.Surface:
    w, h = size
    s = pygame.Surface((w, h))
    s.fill(NAVY)
    step = 32
    for x in range(0, w, step):
        pygame.draw.line(s, GRID, (x, 0), (x, h), 1)
    for y in range(0, h, step):
        pygame.draw.line(s, GRID, (0, y), (w, y), 1)
    # inlaid compass, upper left
    cx, cy, rad = 96, 96, 54
    pygame.draw.circle(s, BRASS, (cx, cy), rad, 2)
    pygame.draw.circle(s, LINE, (cx, cy), rad - 10, 1)
    pygame.draw.line(s, GOLD, (cx, cy + 8), (cx + 6, cy - rad + 14), 3)
    pygame.draw.line(s, STEEL, (cx, cy + 8), (cx - 4, cy + rad - 16), 2)
    pygame.draw.circle(s, INK, (cx, cy + 8), 3)
    # steel ruler, near edge
    pygame.draw.rect(s, STEEL, (48, h - 56, w - 160, 18), 0)
    pygame.draw.rect(s, WOOD, (48, h - 56, w - 160, 18), 1)
    for i in range(0, w - 220, 24):
        x = 56 + i
        tall = 10 if i % 120 == 0 else 6
        pygame.draw.line(s, NAVY, (x, h - 56), (x, h - 56 + tall), 1)
    # USB in the wood, right side — unjustified, as written
    pygame.draw.rect(s, USB, (w - 78, h // 2 - 10, 36, 20), 0, border_radius=2)
    pygame.draw.rect(s, STEEL, (w - 70, h // 2 - 4, 16, 8), 0)
    return s


def tick_geometry():
    x0, x1, y = 160, 1380, 420
    n = 12
    xs = [x0 + i * (x1 - x0) / (n - 1) for i in range(n)]
    return x0, x1, y, n, xs


def draw_ticks(s, font_s, font_xs, upto: int, show_n: bool, finite_p: float):
    x0, x1, y, n, xs = tick_geometry()
    pygame.draw.line(s, INK, (x0 - 20, y), (x1 + 40, y), 3)
    last = min(n, upto)
    for i in range(last):
        x = xs[i]
        pygame.draw.line(s, INK, (x, y - 18), (x, y + 18), 2)
        label = "N" if (i == n - 1 and show_n) else str(i + 1)
        blit_text(s, font_xs, label, (x, y + 26), PALE, "c")
    if finite_p > 0:
        write_chars(s, font_s, "finite", (xs[-1] + 18, y - 54), GOLD, finite_p)


def scene_sheldon_ticks(progress: float) -> pygame.Surface:
    s = table()
    f, xs, sm = _font(FONT, 36), _font(FONT, 20), _font(FONT_S, 28)
    blit_text(s, sm, "sequence  —  not a container", (80, 36), PALE)
    # ticks appear left to right, then the word finite
    tick_p = min(1.0, progress / 0.7)
    finite_p = max(0.0, (progress - 0.7) / 0.3)
    n_show = max(1, int(round(12 * tick_p)))
    draw_ticks(s, f, xs, n_show, show_n=n_show >= 12, finite_p=finite_p)
    blit_text(s, xs, "1 … N   discrete tokens. Probability is a product along the line.", (160, 560), PALE)
    return s


def scene_chi_bracket(progress: float) -> pygame.Surface:
    s = table()
    f, xs, sm, big = _font(FONT, 36), _font(FONT, 20), _font(FONT_S, 28), _font(FONT_B, 64)
    blit_text(s, sm, "χ  is the span that carries him", (80, 36), PALE)
    draw_ticks(s, f, xs, 12, True, 1.0)
    x0, x1, y, n, pts = tick_geometry()
    a, b = pts[3], pts[8]
    # bracket grows
    width = (b - a) * min(1.0, progress / 0.55)
    pygame.draw.line(s, GOLD, (a, y + 70), (a + width, y + 70), 3)
    if progress > 0.2:
        pygame.draw.line(s, GOLD, (a, y + 58), (a, y + 70), 3)
    if progress > 0.5:
        pygame.draw.line(s, GOLD, (a + width, y + 58), (a + width, y + 70), 3)
    chi_p = max(0.0, (progress - 0.55) / 0.45)
    write_chars(s, big, "χ", ((a + b) // 2, y + 86), GOLD, chi_p)
    if progress > 0.75:
        blit_text(s, xs, "attention mass = sum of weights on the ticks inside the bracket", (160, 720), PALE)
    return s


def scene_softmax(progress: float) -> pygame.Surface:
    s = table()
    f, sm, eq = _font(FONT, 22), _font(FONT_S, 28), _font(FONT, 42)
    blit_text(s, sm, "weights are a softmax. at a position they sum to one.", (80, 36), PALE)
    blit_text(s, sm, "that sum is the capacity. it is a budget.", (80, 76), PALE)
    formulas = [
        "w_i  =  exp(z_i)  /  Σ_j exp(z_j)",
        "Σ_i w_i  =  1",
        "anything new that earns mass takes the mass off him",
    ]
    y = 220
    for i, line in enumerate(formulas):
        p = min(1.0, max(0.0, (progress - i * 0.28) / 0.28))
        write_chars(s, eq if i < 2 else f, line, (160, y), GOLD if i == 1 else INK, p)
        y += 90
    # bars that always sum to 1
    if progress > 0.4:
        masses = [0.42, 0.18, 0.27, 0.13]
        x, y0 = 160, 620
        tot = 0.0
        for m, col in zip(masses, (GOLD, PALE, INK, RED)):
            bw = int(980 * m * min(1.0, (progress - 0.4) / 0.6))
            pygame.draw.rect(s, col, (x + int(980 * tot), y0, bw, 36))
            tot += m
        blit_text(s, f, "Σ = 1", (1160, y0 + 4), GOLD)
    return s


def scene_halflife(progress: float) -> pygame.Surface:
    s = table()
    sm, f, eq = _font(FONT_S, 26), _font(FONT, 22), _font(FONT, 40)
    blit_text(s, sm, "null: no one says the name. no query lands on the span.", (80, 36), PALE)
    blit_text(s, sm, "uniform mass on a fixed width falls as 1/t. width cancels.", (80, 76), PALE)
    # 1/t curve
    x0, y0, x1, y1 = 140, 780, 980, 220
    pts = []
    t_max = 12.0
    for px in range(x0, x1):
        t = 1.0 + (t_max - 1.0) * (px - x0) / (x1 - x0)
        m = 1.0 / t
        py = int(y0 - (y0 - y1) * m)
        pts.append((px, py))
    drawn = max(2, int(len(pts) * min(1.0, progress / 0.55)))
    if drawn >= 2:
        pygame.draw.lines(s, GOLD, False, pts[:drawn], 3)
    pygame.draw.line(s, LINE, (x0, y0), (x1, y0), 1)
    pygame.draw.line(s, LINE, (x0, y0), (x0, y1), 1)
    blit_text(s, f, "t", (x1 + 8, y0 - 8), PALE)
    blit_text(s, f, "mass", (x0 - 10, y1 - 24), PALE)
    # half-life construction
    if progress > 0.45:
        t_half = 2.0
        px = int(x0 + (x1 - x0) * (t_half - 1.0) / (t_max - 1.0))
        py = int(y0 - (y0 - y1) * (1.0 / t_half))
        pygame.draw.line(s, RED, (px, y0), (px, py), 1)
        pygame.draw.line(s, RED, (x0, py), (px, py), 1)
        blit_text(s, f, "½", (x0 + 8, py - 28), RED)
    p = max(0.0, (progress - 0.55) / 0.45)
    write_chars(s, eq, "t_{1/2}  =  current context length", (140, 840), INK, p)
    write_chars(s, f, "not a constant. an exponential kernel would be required. he does not have one.", (140, 900), PALE, p)
    return s


def scene_cut(progress: float) -> pygame.Surface:
    s = table()
    f, xs, sm = _font(FONT, 36), _font(FONT, 20), _font(FONT_S, 28)
    blit_text(s, sm, "past N the span is not thinned. the ticks leave the tape.", (80, 36), PALE)
    draw_ticks(s, f, xs, 12, True, 1.0)
    x0, x1, y, n, pts = tick_geometry()
    cut_x = pts[-1]
    # cut mark drops
    drop = int(80 * min(1.0, progress / 0.4))
    pygame.draw.line(s, RED, (cut_x + 28, y - 50), (cut_x + 28, y + 30 + drop), 3)
    blit_text(s, xs, "cut", (cut_x + 40, y - 70), RED)
    gone = max(0.0, (progress - 0.4) / 0.6)
    # ghost ticks sliding off
    for k in range(3):
        gx = int(cut_x + 70 + k * 46 + gone * 80)
        alpha = max(40, int(200 * (1.0 - gone)))
        ghost = pygame.Surface((8, 40), pygame.SRCALPHA)
        ghost.fill((*STEEL, alpha))
        s.blit(ghost, (gx, y - 20))
    if progress > 0.7:
        blit_text(s, xs, "eviction. both endings are on the sheet. the rectangles had neither.", (160, 620), PALE)
    return s


def scene_ted_rectangles(progress: float) -> pygame.Surface:
    s = table()
    sm, f = _font(FONT_S, 28), _font(FONT, 22)
    blit_text(s, sm, "Ted: nested rectangles. containment called a model.", (80, 36), PALE)
    # inner then outer
    inner = pygame.Rect(420, 280, 280, 200)
    outer = pygame.Rect(280, 180, 560, 420)
    if progress > 0.15:
        pygame.draw.rect(s, INK, outer, 3)
    if progress > 0.35:
        pygame.draw.rect(s, GOLD, inner, 3)
    # arrow, then moved 2mm (~8px at this scale)
    if progress > 0.55:
        shift = 8 if progress > 0.78 else 0
        pygame.draw.line(s, PENCIL, (inner.right, inner.centery), (outer.right - 24 + shift, inner.centery), 2)
        pygame.draw.polygon(
            s, PENCIL,
            [(outer.right - 24 + shift, inner.centery),
             (outer.right - 40 + shift, inner.centery - 8),
             (outer.right - 40 + shift, inner.centery + 8)],
        )
        if progress > 0.78:
            blit_text(s, f, "arrow moved 2 mm. the arrow was not the problem.", (280, 640), PALE)
    return s


def scene_ted_deed(progress: float) -> pygame.Surface:
    s = table()
    sm, f, xs = _font(FONT_S, 26), _font(FONT, 36), _font(FONT, 20)
    blit_text(s, sm, "a rectangle around Sheldon's line, and another beyond it.", (80, 36), PALE)
    x0, x1, y, n, pts = tick_geometry()
    y = 480
    pygame.draw.line(s, INK, (x0, y), (x1, y), 3)
    for x in pts:
        pygame.draw.line(s, INK, (x, y - 12), (x, y + 12), 2)
    inner = pygame.Rect(x0 - 30, y - 90, (x1 - x0) + 60, 180)
    outer = pygame.Rect(x0 - 110, y - 200, (x1 - x0) + 220, 400)
    if progress > 0.2:
        pygame.draw.rect(s, GOLD, inner, 2)
    if progress > 0.45:
        pygame.draw.rect(s, PALE, outer, 2)
        blit_text(s, xs, "address / record", (outer.right - 8, outer.top + 8), PALE, "tr")
        blit_text(s, xs, "the room", (inner.centerx, inner.top + 8), GOLD, "c")
    # narrow deed line inner to outer
    if progress > 0.65:
        pygame.draw.line(s, RED, (inner.centerx, inner.top), (inner.centerx, outer.top + 4), 2)
        write_chars(s, xs, "deed  —  not made of the same material as the room", (x0, outer.bottom + 16), RED, (progress - 0.65) / 0.35)
    return s


def scene_fraction(progress: float) -> pygame.Surface:
    s = table()
    sm, eq = _font(FONT_S, 28), _font(FONT, 56)
    blit_text(s, sm, "the bar of the fraction. a page turns. it comes out off level.", (80, 36), PALE)
    cx, cy = W // 2, 480
    tilt = 11 * (1.0 - min(1.0, max(0.0, (progress - 0.45) / 0.4)))
    if progress < 0.45:
        tilt = 11.0
    rad = math.radians(tilt)
    half = 180
    dx, dy = half * math.cos(rad), half * math.sin(rad)
    pygame.draw.line(s, INK, (cx - dx, cy - dy), (cx + dx, cy + dy), 5)
    blit_text(s, eq, "1", (cx, cy - 90), INK, "c")
    blit_text(s, eq, "t", (cx, cy + 24), INK, "c")
    if progress > 0.85:
        blit_text(s, sm, "he redraws it. he does not look at the couch.", (80, 820), PALE)
    return s


SCENES = {
    "sheldon_ticks": scene_sheldon_ticks,
    "chi_bracket": scene_chi_bracket,
    "sheldon_softmax": scene_softmax,
    "sheldon_halflife": scene_halflife,
    "sheldon_cut": scene_cut,
    "ted_rectangles": scene_ted_rectangles,
    "ted_deed": scene_ted_deed,
    "sheldon_fraction": scene_fraction,
}

# Measured: abstracts as printed. Sources fetched 2026-10-29.
# Dukas & Ellner: Ecology 74(5) 1337–1346, author PDF (McMaster).
# Bundesen: Psychological Review 97(4) 523–547, Europe PMC PMID 2247540.
# Tversky: Psychological Review 84(4) 327–352, APA / UCSD PDF.
# Luce: Individual Choice Behavior, Wiley 1959, PsycNET 1960-03588-000.

PAPERS_DATA = [
    {
        "id": "ross_dukas",
        "journal": "ECOLOGY",
        "vol": "Vol. 74, No. 5  ·  July 1993  ·  pp. 1337–1346",
        "doi": "doi:10.2307/1940064",
        "title": "Information Processing and Prey Detection",
        "authors": "Reuven Dukas  ·  Stephen Ellner",
        "affil": "North Carolina State University",
        "abstract": (
            "We present a model to examine how foragers should divide attention among "
            "different potential prey types in order to maximize their net rate of "
            "energy intake. We define attention as the brain's capacity to process "
            "information simultaneously. Our model is based on neuropsychological "
            "studies suggesting first, that predators who divide attention among an "
            "increasing number of different prey types decrease their ability to "
            "detect any given type, and second, that this decrease is larger when "
            "prey items are more difficult to detect. Our model also incorporates "
            "the effects of search rate on forager's probability to detect prey. "
            "The model predicts that foragers encountering cryptic prey should "
            "devote all attention to a single prey type. When encountering "
            "conspicuous prey, foragers should divide attention among the different "
            "prey types. For prey types that differ in conspicuousness but are "
            "equal in energy content, handling time, and density, foragers should "
            "give more attention to the more conspicuous prey if the "
            "conspicuousness values of all prey types are relatively small. "
            "However, when all prey are more conspicuous, foragers should devote "
            "more attention to the less conspicuous prey type. We suggest that our "
            "model may serve to explain and predict some of the foraging decisions "
            "of animals searching for cryptic or conspicuous prey, and especially "
            "studies on “search image” formation."
        ),
        "note": "Ross: limited attention in foraging. Not a clock. Competition.",
    },
    {
        "id": "ross_bundesen",
        "journal": "PSYCHOLOGICAL REVIEW",
        "vol": "Vol. 97, No. 4  ·  October 1990  ·  pp. 523–547",
        "doi": "doi:10.1037/0033-295X.97.4.523",
        "title": "A Theory of Visual Attention",
        "authors": "Claus Bundesen",
        "affil": "Psychological Laboratory, Copenhagen University",
        "abstract": (
            "A unified theory of visual recognition and attentional selection is "
            "developed by integrating the biased-choice model for single-stimulus "
            "recognition (Luce, 1963; Shepard, 1957) with a choice model for "
            "selection from multielement displays (Bundesen, Pedersen, & Larsen, "
            "1984) in a race model framework. Mathematically, the theory is "
            "tractable, and it specifies the computations necessary for selection. "
            "The theory is applied to extant findings from a broad range of "
            "experimental paradigms. The findings include effects of object "
            "integrality in selective report, number and spatial position of "
            "targets in divided-attention paradigms, selection criterion and "
            "number of distracters in focused-attention paradigms, delay of "
            "selection cue in partial report, and consistent practice in search. "
            "On the whole, the quantitative fits are encouraging."
        ),
        "note": "Ross: TVA sits on a Luce choice rule. P(i) = v(i) / Σ v.",
    },
    {
        "id": "ross_luce",
        "journal": "JOHN WILEY  ·  NEW YORK",
        "vol": "1959  ·  153 pages",
        "doi": "PsycNET 1960-03588-000",
        "title": "Individual Choice Behavior: A Theoretical Analysis",
        "authors": "R. Duncan Luce",
        "affil": "",
        "abstract": (
            "This research monograph is devoted to a theoretical (mathematical) "
            "analysis of one of the major themes of interest to psychologists: "
            "choice. The analysis begins by stating a general axiom that may hold "
            "among the probabilities of choice from related sets of alternatives. "
            "This is shown to imply the existence of a ratio scale that is then "
            "used to analyze a number of traditional problems. One consequence is "
            "the ratio rule: if alternatives have positive strengths, the "
            "probability of selecting i from S is v(i) divided by the sum of "
            "v(j) over j in S. The book treats psychophysics, utility, and "
            "learning; the zero-strength case is part of the axiom, not an afterthought."
        ),
        "note": "Ross: the formalism Sheldon wants. Choice, not decay.",
    },
    {
        "id": "ross_tversky",
        "journal": "PSYCHOLOGICAL REVIEW",
        "vol": "Vol. 84, No. 4  ·  July 1977  ·  pp. 327–352",
        "doi": "doi:10.1037/0033-295X.84.4.327",
        "title": "Features of Similarity",
        "authors": "Amos Tversky",
        "affil": "Hebrew University, Jerusalem",
        "abstract": (
            "The metric and dimensional assumptions that underlie the geometric "
            "representation of similarity are questioned on both theoretical and "
            "empirical grounds. A new set-theoretical approach to similarity is "
            "developed in which objects are represented as collections of features, "
            "and similarity is described as a feature-matching process. Specifically, "
            "a set of qualitative assumptions is shown to imply the contrast model, "
            "which expresses the similarity between objects as a linear combination "
            "of the measures of their common and distinctive features. Several "
            "predictions of the contrast model are tested in studies of similarity "
            "with both semantic and perceptual stimuli. The model is used to "
            "uncover, analyze, and explain a variety of empirical phenomena such as "
            "the role of common and distinctive features, the relations between "
            "judgments of similarity and difference, the presence of asymmetric "
            "similarities, and the effects of context on judgments of similarity. "
            "The contrast model generalizes standard representations of similarity "
            "data in terms of clusters and trees. It is also used to analyze the "
            "relations of prototypicality and family resemblance."
        ),
        "note": "Ross: the match is asymmetric. Refresh has a direction.",
    },
]


def paper_surface(row: dict) -> pygame.Surface:
    s = pygame.Surface((PAPER_W, PAPER_H))
    s.fill((48, 42, 38))
    # sheet
    margin = 70
    sheet = pygame.Rect(margin, 28, PAPER_W - 2 * margin, PAPER_H - 70)
    pygame.draw.rect(s, CREAM, sheet)
    pygame.draw.rect(s, (210, 198, 170), sheet, 2)
    # fingers holding the bottom edge
    for fx in (sheet.left + 80, sheet.centerx - 20, sheet.right - 140):
        pygame.draw.ellipse(s, HAND, (fx, sheet.bottom - 8, 54, 36))
        pygame.draw.ellipse(s, (140, 108, 84), (fx, sheet.bottom - 8, 54, 36), 1)
    x = sheet.left + 36
    y = sheet.top + 18
    jrn = _font(FONT_SB, 15)
    tit = _font(FONT_SB, 26)
    auth = _font(FONT_SI, 18)
    body = _font(FONT_S, 16)
    tiny = _font(FONT, 13)
    blit_text(s, jrn, row["journal"], (x, y), RULE)
    y += 22
    blit_text(s, tiny, row["vol"], (x, y), MUTED)
    blit_text(s, tiny, row["doi"], (sheet.right - 36, y), MUTED, "tr")
    y += 20
    pygame.draw.line(s, RULE, (x, y), (sheet.right - 36, y), 2)
    y += 14
    # title wrap
    wrap_w = sheet.width - 72
    for line in textwrap.wrap(row["title"], width=48):
        blit_text(s, tit, line, (x, y), INK_K)
        y += 32
    blit_text(s, auth, row["authors"], (x, y), INK_K)
    y += 24
    if row["affil"]:
        blit_text(s, tiny, row["affil"], (x, y), MUTED)
        y += 20
    blit_text(s, jrn, "ABSTRACT", (x, y), RULE)
    y += 22
    for line in textwrap.wrap(row["abstract"], width=92):
        blit_text(s, body, line, (x, y), INK_K)
        y += 20
        if y > sheet.bottom - 70:
            break
    blit_text(s, tiny, row["note"], (x, sheet.bottom - 36), MUTED)
    return s


def save(surf: pygame.Surface, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(dest))
    print(f"  {dest.relative_to(BASE)}  {dest.stat().st_size}", flush=True)


def cmd_stills(_args=None):
    pygame.init()
    OUT.mkdir(parents=True, exist_ok=True)
    for sid, fn in SCENES.items():
        save(fn(1.0), OUT / f"{sid}.png")
    # aliases the 07k still pool already names
    save(SCENES["sheldon_halflife"](1.0), OUT / "sheldon_ticks_null.png")
    cmd_papers()
    pygame.quit()


def cmd_papers(_args=None):
    pygame.init()
    PAPERS.mkdir(parents=True, exist_ok=True)
    for row in PAPERS_DATA:
        surf = paper_surface(row)
        save(surf, PAPERS / f"{row['id']}.png")
        save(surf, OUT / f"{row['id']}.png")
    # generic ross_paper = first held sheet (Dukas), then assemble keywords pick the rest
    save(paper_surface(PAPERS_DATA[0]), OUT / "ross_paper.png")
    pygame.quit()


def cmd_anim(_args=None):
    pygame.init()
    n = 16
    for sid, fn in SCENES.items():
        d = ANIM / sid
        d.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            p = (i + 1) / n
            save(fn(p), d / f"{i:02d}.png")
    pygame.quit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "anim", "papers", "all"], nargs="?", default="all")
    args = ap.parse_args()
    if args.cmd in ("stills", "all"):
        cmd_stills()
    if args.cmd in ("papers",) and args.cmd != "all":
        cmd_papers()
    if args.cmd in ("anim", "all"):
        cmd_anim()


if __name__ == "__main__":
    main()

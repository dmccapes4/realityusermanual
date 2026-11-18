#!/usr/bin/env python3
"""Build dylanmccapes.systems/expression for The   Bed."""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parent.parent
DEV = BASE.parent
STAR = DEV / "star_learning"
POEM = DEV / "docs/library/personal/poems/TheBed"
SITE = BASE / "web/expression"
FILES = SITE / "files"
MEDIA = SITE / "media"
IMAGES = SITE / "images/files"
AUDIO = SITE / "audio/files"
CHAPTER_MEDIA = SITE / "last-chapter/media"

TITLE = "The   Bed"
BUILD_VERSION = int(time.time())
VIDEO = BASE / "video/minus36/-36_the_bed.mp4"
MANIFEST = BASE / "video/minus36/manifest.json"
CUES = BASE / "audio/minus36/cues.jsonl"

POEM_MD = POEM / '"The `\\(Godot)\\` Bed".py?.c.md.md'
SOURCE_C = POEM / "still_yet_unarrived.c"
WALKTHROUGH = POEM / "TerminalWalkthrough"
EPILOGUE = POEM / "epilogue.txt"
CATALOG = POEM / "TheBed_images/CATALOG.md"

AUDIO_SOURCES = [
    ("hi-frances", "Hi Frances", BASE / "audio/HiFrances.m4a"),
    ("hi-juju", "Hi Juju", BASE / "audio/HiJuju.m4a"),
    ("the-bed", TITLE, BASE / "audio/TheBed.m4a"),
    ("soon-unity", "Soon Unity", BASE / "audio/SoonUnity.m4a"),
]

HI_FRANCES = """Hi Frances,

I love you so much. I want to be with you. Right now Mama will not let me. She told people that I am not safe to be around. She is trying to be a good Mom, but it is not true. Now people are pressuring me to be with you under supervision — where a lady we don't know judges us and takes notes. I do not want you to be in such a situation because I am safe, and it is unnecessary. I don't want you to get the false impression that I am not safe or capable of being with you alone. If you are ok with this then we will wait till December or when Mama says it is ok. If you want to see me sooner then I need to know that you understand the arrangement. That is the only way it is ethical. Which is good. I love you."""

HI_JUJU = """Hey Juju!

I love you so much, and I miss you so much. I will be with you the very minute I am able to once Mama lets me.

I have been building your game. Dada was silly and tried to build the animal shapes in Godot which means "absent character", but now he is building the animal shapes with Unity which means "all of us Together"."""

THE_BED = """I’ve learned that a heart breaks like ionic decay.
Sharply at first then steadily then it ever approaches
the deepest depth the despair designed by decline;
Already at asymptotic limit
yet each day more even upon her deathly bed.
Now again the cushion yet bends a sepulcher net."""


def ffprobe(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def link_or_copy(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    try:
        os.link(source, dest)
    except OSError:
        shutil.copy2(source, dest)


def stamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def nav(active: str) -> str:
    links = [
        ("film", "/expression/", "Film"),
        ("work", "/expression/the___bed/", "The .md"),
        ("images", "/expression/images/", "Images"),
        ("audio", "/expression/audio/", "Audio"),
        ("transcript", "/expression/transcript/", "Transcript"),
        ("last-chapter", "/expression/last-chapter/", "Last chapter"),
    ]
    return "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for key, href, label in links
    )


def page(title: str, active: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#050908">
<title>{html.escape(title)} — Expression — the operator</title>
<link rel="stylesheet" href="/expression/expression.css?v={BUILD_VERSION}">
</head>
<body>
<header>
  <a class="site" href="/">dylanmccapes.systems</a>
  <p class="kicker">EXPRESSION / THE OPERATOR</p>
  <h1><code>The&nbsp;&nbsp;&nbsp;Bed</code></h1>
  <nav>{nav(active)}</nav>
</header>
<main>{body}</main>
<footer>Source, execution, voice, and image remain available together.</footer>
</body>
</html>
"""


def write_css() -> None:
    (SITE / "expression.css").write_text(
        """
:root{--bg:#050908;--panel:#0b1210;--line:#22332d;--ink:#e8eee8;--muted:#92a29a;--green:#28d17c;--gold:#e8c55b}
*{box-sizing:border-box}html{background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,sans-serif}
body{margin:0;background:radial-gradient(900px 480px at 70% -10%,#163024 0,transparent 65%),var(--bg)}
header,main,footer{width:min(1120px,calc(100% - 32px));margin:auto}header{padding:42px 0 20px}
.site{color:var(--muted);text-decoration:none}.kicker{font:12px ui-monospace,monospace;letter-spacing:.18em;color:var(--green);margin:22px 0 7px}
h1{font-size:clamp(34px,7vw,72px);margin:0 0 22px;line-height:1}h1 code{font:inherit}
nav{display:flex;gap:8px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:14px}
nav a,.button{color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:8px 12px;border-radius:999px}
nav a.active,nav a:hover,.button:hover{color:var(--ink);border-color:var(--green)}
main{padding:24px 0 72px}.lede{font-size:clamp(18px,3vw,26px);max-width:760px;color:#cbd6cf}
.film{width:100%;height:auto;aspect-ratio:16/9;object-fit:contain;background:#000;border:1px solid var(--line);border-radius:12px;box-shadow:0 20px 70px #000;display:block}
.system-note{color:var(--muted);margin:10px 0 22px}
.links,.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:24px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px;color:var(--ink);text-decoration:none}
.card small{display:block;color:var(--green);font:11px ui-monospace,monospace;letter-spacing:.12em;margin-bottom:7px}
.card p{color:var(--muted);margin:6px 0}.source{background:#080d0b;border:1px solid var(--line);padding:24px;border-radius:10px;overflow:auto}
.source pre,pre.source{white-space:pre-wrap;font:14px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace}
.rendered{max-width:820px}.rendered h1,.rendered h2,.rendered h3{font-size:1.2rem;color:var(--gold)}
.rendered pre{white-space:pre-wrap;overflow:auto;background:#080d0b;padding:16px;border:1px solid var(--line)}
.rendered code{font-family:ui-monospace,monospace}.gallery{columns:3 260px;column-gap:12px}
.gallery figure{break-inside:avoid;margin:0 0 12px;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.gallery img{width:100%;height:auto;display:block}.gallery figcaption{padding:8px 10px;color:var(--muted);font-size:12px}
audio{width:100%;margin-top:12px}.transcript article{border-left:2px solid var(--line);padding:0 0 22px 18px;margin:0 0 22px}
.transcript time{font:12px ui-monospace,monospace;color:var(--green)}.transcript h2{margin:5px 0 9px}.transcript p{white-space:pre-wrap;color:#cbd6cf}
.chapter{max-width:1000px}.chapter>section{padding:32px 0;border-top:1px solid var(--line)}
.chapter h2{font-size:clamp(25px,4vw,38px);margin:0 0 12px}.chapter h3{color:var(--gold);margin:8px 0}
.chapter p{color:#cbd6cf;line-height:1.65}.chapter .chapter-lede{font-size:clamp(19px,3vw,27px);color:var(--ink)}
.chapter-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin:20px 0}
.chapter figure{margin:18px 0;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.chapter figure img,.chapter figure video{width:100%;height:auto;display:block;background:#000}
.chapter figcaption{padding:12px 15px;color:var(--muted);font-size:13px;line-height:1.5}
.metric{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px}
.metric strong{display:block;color:var(--green);font:20px ui-monospace,monospace;margin-bottom:8px}
.sequence{font:clamp(18px,4vw,34px) ui-monospace,monospace;color:var(--gold);letter-spacing:.04em;padding:24px;background:#080d0b;border:1px solid var(--line);border-radius:10px;text-align:center}
.receipt{font:13px/1.55 ui-monospace,monospace;color:var(--muted);overflow-wrap:anywhere}
footer{border-top:1px solid var(--line);padding:22px 0 50px;color:var(--muted);font-size:13px}
@media(max-width:600px){header{padding-top:24px}.source{padding:14px}}
""".strip() + "\n",
        encoding="utf-8",
    )


def copy_sources() -> list[tuple[str, str, str]]:
    sources = [
        (POEM_MD, "the___bed.md", "Markdown source"),
        (SOURCE_C, "still_yet_unarrived.c", "Executable source"),
        (WALKTHROUGH, "terminal_walkthrough.txt", "Terminal walkthrough"),
        (EPILOGUE, "epilogue.txt", "Epilogue"),
        (CATALOG, "image_catalog.md", "Image catalog"),
    ]
    result = []
    for source, name, label in sources:
        shutil.copy2(source, FILES / name)
        result.append((name, label, source.name))
    return result


def image_sources() -> list[tuple[Path, str]]:
    cards = POEM / "TheBed_images"
    result = [(cards / f"IMG_{n}.jpg", f"card-{n}.jpg") for n in (1511, 1512, 1513, 1514)]
    epilogue = cards / "epilogue"
    for index, source in enumerate(sorted(epilogue.glob("*.jpg")), 1):
        clean = re.sub(r"[^a-z0-9]+", "-", source.stem.lower()).strip("-")
        result.append((source, f"epilogue-{index:02d}-{clean}.jpg"))
    return result


def transcript_cues() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    starts: dict[str, float] = {}
    cursor = 0.0
    for rel in manifest["clips"]:
        clip = BASE / rel
        starts[clip.name] = cursor
        cursor += ffprobe(clip)

    cues: list[dict] = [
        {
            "start": starts["03_frances.mp4"],
            "end": starts["03_frances.mp4"] + ffprobe(BASE / "audio/HiFrances.m4a"),
            "speaker": "the operator",
            "title": "Hi Frances",
            "text": HI_FRANCES,
        },
        {
            "start": starts["04_juju.mp4"],
            "end": starts["04_juju.mp4"] + ffprobe(BASE / "audio/HiJuju.m4a"),
            "speaker": "the operator",
            "title": "Hi Juju",
            "text": HI_JUJU,
        },
        {
            "start": starts["05_bed.mp4"],
            "end": starts["05_bed.mp4"] + ffprobe(BASE / "audio/TheBed.m4a"),
            "speaker": "the operator",
            "title": TITLE,
            "text": THE_BED,
        },
    ]
    for raw in CUES.read_text(encoding="utf-8").splitlines():
        cue = json.loads(raw)
        name = f"tech_{cue['index']:02d}.mp4"
        cues.append(
            {
                "start": starts[name],
                "end": starts[name] + cue["duration"],
                "speaker": cue["speaker"],
                "title": cue["title"],
                "text": cue["text"],
            }
        )
    soon = EPILOGUE.read_text(encoding="utf-8").strip()
    cues.append(
        {
            "start": starts["100_epilogue_history.mp4"],
            "end": starts["100_epilogue_history.mp4"] + ffprobe(BASE / "audio/SoonUnity.m4a"),
            "speaker": "the operator",
            "title": "Soon Unity",
            "text": soon,
        }
    )
    return sorted(cues, key=lambda cue: cue["start"])


def write_transcript(cues: list[dict]) -> None:
    vtt = ["WEBVTT", ""]
    txt = []
    articles = []
    for index, cue in enumerate(cues, 1):
        start, end = cue["start"], cue["end"]
        vtt += [
            str(index),
            f"{stamp(start)} --> {stamp(end)}",
            f"{cue['speaker']}: {cue['text']}",
            "",
        ]
        txt.append(
            f"[{stamp(start)}] {cue['speaker']} — {cue['title']}\n{cue['text']}"
        )
        articles.append(
            f"<article><time>{stamp(start)}</time>"
            f"<h2>{html.escape(cue['title'])}</h2>"
            f"<strong>{html.escape(cue['speaker'])}</strong>"
            f"<p>{html.escape(cue['text'])}</p></article>"
        )
    (SITE / "transcript.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (SITE / "transcript.txt").write_text("\n\n".join(txt) + "\n", encoding="utf-8")
    body = (
        '<p class="lede">The operator recordings and Matilda’s technical examination, '
        'in film order.</p><p><a class="button" href="/expression/transcript.txt">'
        "Download plain text</a></p>"
        f'<section class="transcript">{"".join(articles)}</section>'
    )
    out = SITE / "transcript/index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page("Transcript", "transcript", body), encoding="utf-8")


def write_last_chapter() -> None:
    assets = {
        "ant-video.mp4": STAR / "ant_explorer/docs/demo/ant_explorer_homeostasis.mp4",
        "larval-space.png": STAR / "ant_explorer/docs/demo/homeostasis_frames/02_larval.png",
        "surplus-correction.png": STAR / "ant_explorer/docs/demo/homeostasis_frames/04_surplus_late.png",
        "zecliptic-flight.mp4": STAR / "solar_system_explorer/docs/demo/zecliptic_angle_flight.mp4",
        "mars-flower-track.png": STAR / "solar_system_explorer/docs/THEBES_MARS_M44_2400BC/mars_retrograde_track_thebes_2400bc.png",
        "thebes-sky.png": STAR / "solar_system_explorer/docs/THEBES_MARS_M44_2400BC/sky_view_thebes_mars_m44.png",
        "pollux-arc.png": STAR / "solar_system_explorer/docs/WINTER_CIRCLE_CATS_EYES_20261009/strategy_5_pollux_arc.png",
        "zecliptic-strip.png": STAR / "solar_system_explorer/docs/WINTER_CIRCLE_CATS_EYES_20261009/ext_view4_zecliptic_strip.png",
    }
    CHAPTER_MEDIA.mkdir(parents=True, exist_ok=True)
    for name, source in assets.items():
        if source.suffix == ".mp4":
            link_or_copy(source, CHAPTER_MEDIA / name)
        else:
            shutil.copy2(source, CHAPTER_MEDIA / name)

    body = f"""
<article class="chapter">
  <h2>The Last Chapter</h2>
  <p class="chapter-lede">The story ends. The field that produced it keeps opening.</p>
  <p>This companion chapter sits outside the film. It follows the work from a larval control space into a research station for changing the observer, the epoch, and the sky.</p>

  <section>
    <h2>From larvae to trigger vectors</h2>
    <p>Ant Explorer runs each larva through nutrition, juvenile hormone, age, colony demand, and caste pressure. Those variables do not merely describe the larva: they bend thresholds, trigger pupation, and redirect future work. The operator calls this reusable arrangement a <em>trigger vector</em>—a compact state whose position can cause a different system to change course.</p>
    <p>Later systems reuse the method, not the ant metaphor: choose the live variables, preserve their relations, and let the combined state trigger the next transition.</p>
    <figure>
      <video controls playsinline preload="metadata" src="/expression/last-chapter/media/ant-video.mp4?v={BUILD_VERSION}"></video>
      <figcaption>Ant Explorer’s closed loop: census, nutrition, juvenile hormone, caste pressure, urgency, and eclosion.</figcaption>
    </figure>
    <div class="chapter-grid">
      <figure><img loading="lazy" src="/expression/last-chapter/media/larval-space.png?v={BUILD_VERSION}" alt="Ant Explorer larval state display"><figcaption>Larval space: the state variables before the threshold.</figcaption></figure>
      <figure><img loading="lazy" src="/expression/last-chapter/media/surplus-correction.png?v={BUILD_VERSION}" alt="Ant Explorer surplus correction display"><figcaption>Homeostatic correction: colony state bends what happens next.</figcaption></figure>
    </div>
  </section>

  <section>
    <h2>The explorer became a research station</h2>
    <p>Solar System Explorer grew past a tour. Its offline stellar ledger propagates 1,001 offsets from 500,000 years before J2000 to 500,000 years after it. Its planetary viewer occupies a narrower ephemeris window, while its scripts, ledgers, historical reconstructions, and frame controls form the larger station.</p>
    <div class="chapter-grid">
      <div class="metric"><strong>−500,000 years</strong><p>First stellar offset relative to J2000.</p></div>
      <div class="metric"><strong>1,001 states</strong><p>The written long-range stellar ledger.</p></div>
      <div class="metric"><strong>+500,000 years</strong><p>Last stellar offset relative to J2000.</p></div>
    </div>
    <p><small>The long-range star field is exploratory linear propagation. The project itself records tighter reliability limits for fast-moving stars and does not treat the million-year endpoints as precision galactic-orbit solutions.</small></p>
  </section>

  <section>
    <h2>Thebes, October 31</h2>
    <p>At Thebes on October 31, 2553 BC, the reconstruction places retrograde Mars in Dancer (cat. Cancer), beside the Flower (M44, cat. Praesepe / Beehive Cluster), and nearly overhead at transit. The station makes the old astrology spatial again: date, observer, hemisphere, precession, direction, and altitude occupy the same frame.</p>
    <div class="chapter-grid">
      <figure><img loading="lazy" src="/expression/last-chapter/media/mars-flower-track.png?v={BUILD_VERSION}" alt="Computed Mars retrograde track through Dancer near the Flower"><figcaption>Mars reverses through Dancer near the Flower in the computed historical track.</figcaption></figure>
      <figure><img loading="lazy" src="/expression/last-chapter/media/thebes-sky.png?v={BUILD_VERSION}" alt="Computed sky from Thebes with Mars and the Flower near transit"><figcaption>The same event from the Thebes horizon: Mars and the Flower near the zenith.</figcaption></figure>
    </div>
  </section>

  <section>
    <h2>Astronomical prestidigitation</h2>
    <div class="sequence">CASTOR → POLLUX → POLLUX → PROWLSCION = 3.14159 = π</div>
    <p>This is an exact ratio, not an interpretive resemblance. Prowlscion (α CMi, cat. Procyon) closes the four-star arrangement, which resolves to 3.14159. Stars occasionally forming that ratio would hardly be interesting. The curious result is the co-occurrence: the relation holds while Mars is retrograde through Dancer, both on October 31, 2553 BC and again in the later event.</p>
    <p>The later feat is credited to the Babylonian record as 555 AD. The reconstructed sky places it in 557 AD, two years later, with Mars again retrograde through Dancer. The stars themselves form a summation of a circular property; the repeated conjunction of that exact relation with the same planetary motion is the curiosity.</p>
    <p>The operator calls this <em>astronomical prestidigitation</em>: the sky appears to perform a trick, but the receipt is geometry. The Pollux-centered arc plot below shows the field from which the ratio is taken.</p>
    <figure><img loading="lazy" src="/expression/last-chapter/media/pollux-arc.png?v={BUILD_VERSION}" alt="Pollux-centered arc through Castor, Prowlscion, Gameusa and the Flower"><figcaption>Pollux as pivot, with Castor, Prowlscion, Gameusa, and the Flower held in the ratio’s plotted field.</figcaption></figure>
  </section>

  <section>
    <h2>Cydonia in fifteen minutes</h2>
    <p>In roughly fifteen minutes of operator time, the station could leave the present-day anchor, reconstruct the historical Mars orientation, and test Cydonia against the visible disk. At the selected epoch the calculation places Cydonia 65.6° from disk center: visible, 24.4° inside the limb.</p>
    <p>That is the station’s practical time travel: not a claim that fifteen historical minutes passed or that Cydonia crossed the limb in fifteen minutes, but that an observer could move across millennia and ask a geometrically testable visibility question before the quarter-hour was over.</p>
    <div class="chapter-grid">
      <div class="metric"><strong>65.6°</strong><p>Angular distance from the reconstructed disk center.</p></div>
      <div class="metric"><strong>VISIBLE</strong><p>The spherical visibility test returns inside the near hemisphere.</p></div>
      <div class="metric"><strong>24.4°</strong><p>Distance inside the limb.</p></div>
    </div>
  </section>

  <section>
    <h2>The Zecliptic makes the station legible</h2>
    <p>The Zecliptic view exposes what a flat sky chart suppresses: orbital planes, inclinations, body angles, observer position, and the scale changes required to cross the system. It is the station’s geometric grammar.</p>
    <figure>
      <video controls playsinline preload="metadata" src="/expression/last-chapter/media/zecliptic-flight.mp4?v={BUILD_VERSION}"></video>
      <figcaption>The Zecliptic angle-flight: a disorienting descent through the system’s real geometry into Sol.</figcaption>
    </figure>
    <figure><img loading="lazy" src="/expression/last-chapter/media/zecliptic-strip.png?v={BUILD_VERSION}" alt="Stars and Mars oppositions arranged by Zecliptic longitude and latitude"><figcaption>The strip view holds stellar latitude, Mars oppositions, Castor, Pollux, the Flower, and the Cat’s Eyes in one reference plane.</figcaption></figure>
  </section>

  <section>
    <h2>Four Earths, four readings</h2>
    <p>The Earth viewer fixes four observer stations. They are not cosmetic camera presets. Each changes the local vertical, horizon, inversion, transit, and apparent path from which astrology was read.</p>
    <div class="chapter-grid">
      <div class="metric"><strong>−23.5°</strong><h3>Tropic of Capricorn</h3><p>The southern reading and its inverted local vertical.</p></div>
      <div class="metric"><strong>0°</strong><h3>Equator</h3><p>The eclipse station: east–west motion without a northern or southern default.</p></div>
      <div class="metric"><strong>+23.5°</strong><h3>Tropic of Cancer</h3><p>The northern tropic and the latitude carried by Dancer’s inherited catalogue name.</p></div>
      <div class="metric"><strong>38°</strong><h3>Mid-northern</h3><p>The project’s default retrograde station and the operator’s local sky.</p></div>
    </div>
    <p>The station demonstrates that sky orientation changes with the observer. The operator’s further inquiry is linguistic: if different bodies and latitudes repeatedly organize rising, reversal, enclosure, and direction, then those observed relations may be sought in the language that developed around the sky. The viewer supplies the geometry; the philological reading remains the inquiry carried through it.</p>
  </section>

  <section>
    <h2>The door after the ending</h2>
    <p><em>The&nbsp;&nbsp;&nbsp;Bed</em> ends with family images. This last chapter does not alter that ending. It shows what was running beyond the frame: a method learned from larvae, widened into observer geometry, and used to move through a million-year field without pretending every layer has the same kind of proof.</p>
    <p class="receipt">Receipts: ant_explorer/game/scripts/sim/Brood.gd · ant_explorer/game/scripts/sim/Homeostasis.gd · solar_system_explorer/game/tools/star_timeline.py · solar_system_explorer/tools/mars_m44_thebes_2400bc.py · solar_system_explorer/tools/mars_rotation_2554bc.py · solar_system_explorer/game/scripts/ZeclipticFlight.gd · solar_system_explorer/game/scripts/EarthSkyViewer.gd</p>
  </section>
</article>
"""
    out = SITE / "last-chapter/index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page("The Last Chapter", "last-chapter", body), encoding="utf-8")


def build() -> None:
    for path in (SITE, FILES, MEDIA, IMAGES, AUDIO, CHAPTER_MEDIA):
        path.mkdir(parents=True, exist_ok=True)
    write_css()
    source_links = copy_sources()

    link_or_copy(VIDEO, MEDIA / "the___bed.mp4")
    video_version = int(VIDEO.stat().st_mtime)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-ss", "19.0",
            "-i", str(DEV / "star_learning/solar_system_explorer/docs/demo/zecliptic_angle_flight.mp4"),
            "-i", str(POEM / "TheBed_images/wedding_dance.jpg"),
            "-filter_complex",
            (
                "[0:v]scale=1280:720,eq=brightness=-0.18:saturation=0.8[bg];"
                "[1:v]scale=-2:650,pad=iw+10:ih+10:5:5:color=0xe8c55b[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2"
            ),
            "-frames:v", "1",
            "-q:v", "2",
            str(MEDIA / "poster.jpg"),
        ],
        check=True,
    )
    for slug, _, source in AUDIO_SOURCES:
        link_or_copy(source, AUDIO / f"{slug}.m4a")

    files_html = "".join(
        f'<a class="card" href="/expression/files/{name}"><small>{html.escape(label)}</small>'
        f"<strong>{html.escape(name)}</strong><p>{html.escape(original)}</p></a>"
        for name, label, original in source_links
    )
    landing = f"""
<p class="lede">A poem executed across Bash, Python, C, Markdown, voice, family history, and image. Neither rendered nor unrendered is preferred.</p>
<p class="system-note"><small>Terminology: “the operator” is the human author; “agents” are AI collaborators.</small></p>
<video class="film" controls playsinline webkit-playsinline preload="metadata"
       width="1280" height="720" aria-label="The Bed film"
       poster="/expression/media/poster.jpg?v={BUILD_VERSION}">
  <source src="/expression/media/the___bed.mp4?v={video_version}" type="video/mp4">
  <track kind="captions" srclang="en" label="English" src="/expression/transcript.vtt?v={BUILD_VERSION}">
  <p>Your browser could not load the embedded film.</p>
</video>
<p><a class="button" href="/expression/media/the___bed.mp4?v={video_version}">Open film directly</a></p>
<div class="links">
  <a class="card" href="/expression/the___bed/"><small>READ</small><strong>The rendered .md</strong><p>Three spaces remain in the title.</p></a>
  <a class="card" href="/expression/images/"><small>SEE</small><strong>Cards and epilogue</strong><p>The complete image field.</p></a>
  <a class="card" href="/expression/audio/"><small>HEAR</small><strong>Original recordings</strong><p>Four readings by the operator.</p></a>
  <a class="card" href="/expression/transcript/"><small>FOLLOW</small><strong>Film transcript</strong><p>Timed operator and Matilda text.</p></a>
  <a class="card" href="/expression/last-chapter/"><small>CONTINUE</small><strong>The Last Chapter</strong><p>From larval trigger vectors to a million-year research station.</p></a>
</div>
<h2>Files</h2><div class="cards">{files_html}</div>
"""
    (SITE / "index.html").write_text(page(TITLE, "film", landing), encoding="utf-8")

    raw = POEM_MD.read_text(encoding="utf-8")
    rendered = markdown.markdown(
        raw, extensions=["fenced_code", "tables", "nl2br", "sane_lists"]
    )
    work_body = (
        '<p><a class="button" href="/expression/files/the___bed.md">Download .md</a> '
        '<a class="button" href="/expression/files/still_yet_unarrived.c">Download .c</a></p>'
        f'<article class="rendered">{rendered}</article>'
    )
    work = SITE / "the___bed/index.html"
    work.parent.mkdir(parents=True, exist_ok=True)
    work.write_text(page(TITLE, "work", work_body), encoding="utf-8")

    figures = []
    image_manifest = []
    for source, name in image_sources():
        shutil.copy2(source, IMAGES / name)
        category = "Cards" if name.startswith("card-") else "Epilogue"
        figures.append(
            f'<figure><a href="/expression/images/files/{name}">'
            f'<img loading="lazy" src="/expression/images/files/{name}" alt="{html.escape(source.stem)}"></a>'
            f"<figcaption>{category} · {html.escape(source.name)}</figcaption></figure>"
        )
        image_manifest.append(
            {"file": name, "source": source.name, "category": category}
        )
    (SITE / "images/manifest.json").write_text(
        json.dumps(image_manifest, indent=2) + "\n", encoding="utf-8"
    )
    gallery = SITE / "images/index.html"
    gallery.parent.mkdir(parents=True, exist_ok=True)
    gallery.write_text(
        page(
            "Images",
            "images",
            '<p class="lede">The two cards and the family epilogue.</p>'
            f'<section class="gallery">{"".join(figures)}</section>',
        ),
        encoding="utf-8",
    )

    audio_cards = []
    for slug, label, _ in AUDIO_SOURCES:
        audio_cards.append(
            f'<section class="card"><small>ORIGINAL RECORDING</small><strong>{html.escape(label)}</strong>'
            f'<audio controls preload="metadata" src="/expression/audio/files/{slug}.m4a"></audio>'
            f'<p><a class="button" href="/expression/audio/files/{slug}.m4a" download>Download</a></p></section>'
        )
    audio_page = SITE / "audio/index.html"
    audio_page.parent.mkdir(parents=True, exist_ok=True)
    audio_page.write_text(
        page(
            "Audio",
            "audio",
            '<p class="lede">The four operator recordings in the film.</p>'
            f'<div class="cards">{"".join(audio_cards)}</div>',
        ),
        encoding="utf-8",
    )

    write_last_chapter()
    cues = transcript_cues()
    write_transcript(cues)
    print(f"Built {SITE}")
    print(f"Video: {ffprobe(MEDIA / 'the___bed.mp4'):.3f}s")
    print(f"Images: {len(image_manifest)}")
    print(f"Transcript cues: {len(cues)}")


if __name__ == "__main__":
    build()

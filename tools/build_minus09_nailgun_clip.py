#!/usr/bin/env python3
"""Page −09 excerpt — TUROV sign + nailgun review. Semi-realistic slideshow.

Level of realism = video/minus08/stills/players/vincent.png: detailed
semi-realistic graphic-novel painting, realistic faces/anatomy, clean ink,
painted shading. NOT flat Samurai Jack, NOT pygame compositing.

Consistency comes from the script, in this order:
  1. character reference plates (refs/) — generated once, reused
  2. one site reference plate (the same pit / slab / compressor every shot)
  3. every slide is an images/edits call fed its character + site refs,
     with the character bible repeated verbatim

Costumes researched 2026-11-11 (web):
  Stamper  — Armageddon (1998) hero asteroid suit: heavy quilted GREY canvas,
             chest pack with lit controls, backpack, metal neck ring, fibreglass
             helmet with wide visor (Heritage/Propstore). Helmet OFF here.
  Happy    — Happy Gilmore: black Boston Bruins jersey, gold/white striping,
             spoked-B, baggy jeans (Propstore screen-matched jersey).
  Winslade — B.V. Larson, Undying Mercenaries: Tribune (one-star) in cinched
             dark smart-cloth uniform; tapper = bio-grown subcutaneous forearm
             touchscreen, glowing under the skin, which he taps/checks.

  .venv/bin/python tools/build_minus09_nailgun_clip.py refs --render
  .venv/bin/python tools/build_minus09_nailgun_clip.py stills --render
  .venv/bin/python tools/build_minus09_nailgun_clip.py assemble
  .venv/bin/python tools/build_minus09_nailgun_clip.py all --render

Output: video/minus09/-09_turov_nailgun_review.mp4
Full scene: TUROV sign → introductions → nailgun review → Yeshua's nails →
coins → Steps Eight/Nine → approval (end of -09.md, cues 480-687).
The TUROV dual sign is read aloud by Goat (technical / posted-instrument register).
Scene narration (italic/stage) is GoinesFeynman, not The Narrator.
Yeshua, where he appears, has a cat-shaped face with cosmos inside it.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUDIO_MAIN = BASE / "audio" / "minus09"
OUT = BASE / "video" / "minus09"
CLIP = OUT / "clip_nailgun"
REFS = CLIP / "refs"
STILLS = CLIP / "stills_real"
AUDIO_CLIP = CLIP / "minus09_turov_nailgun.mp3"
SIGN_GOOD = OUT / "stills" / "turov_sign_scene.png"  # photoreal dual-sign compose
VINCENT_REF = BASE / "video" / "minus08" / "stills" / "players" / "vincent.png"

CLIP_CUE_FIRST, CLIP_CUE_LAST = 480, 687  # scene runs to the end of -09.md
SIGN_HOLD = 1.0  # second of sign on screen before Goat speaks

_env = BASE / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ── Style + character bible (repeated verbatim in every prompt) ──────────────
STYLE = (
    "Detailed semi-realistic graphic-novel illustration, exactly the register of the "
    "Vincent reference art: realistic human anatomy and fully rendered expressive faces, "
    "clean heavy black ink contours of varying weight, painted colour with cel shading plus "
    "soft painted gradients, detailed fabric, metal and skin texture, cinematic daylight. "
    "NOT flat minimal cartoon, NOT rough sketch, NOT loose brush scumble, NOT a photograph, "
    "NOT anime, NOT 3D CGI. No text, letters or logos in frame except the Bruins spoked-B. "
)

SITE = (
    "THE SAME construction site in every image: a concrete slab work area in the foreground, "
    "a deep excavation pit behind it with a yellow excavator and one tower crane, chain-link "
    "fencing, an orange air compressor on the slab, a plain metal bucket, scattered chalk marks "
    "on the concrete, distant blurred site signage with no readable words, warm late-afternoon light. "
)

VINCENT = (
    "VINCENT — the exact man from the Vincent reference image: slim, late 20s, short neat dark "
    "hair swept back, composed intelligent face, immaculate black single-breasted Gattaca suit, "
    "white dress shirt, narrow black tie, polished black shoes. He never wears anything else. "
)

STAMPER = (
    "HARRY STAMPER — rugged oil driller in his 50s, short greying hair, weathered stubbled face, "
    "broad and tired. He wears his Armageddon asteroid EVA suit: heavy quilted GREY canvas suit, "
    "chest pack with small lit controls, backpack, metal neck ring, rubber pads at knees and elbows, "
    "heavy boots. His fibreglass helmet is OFF — carried under one arm or hanging at his side — "
    "and he holds a clipboard. "
)

HAPPY = (
    "HAPPY GILMORE — athletic late-20s ex-hockey player, shaggy dark hair, intense eager grin, "
    "black Boston Bruins hockey jersey with gold and white sleeve striping and the spoked-B crest, "
    "an unzipped orange hi-vis vest over it on the jobsite, baggy jeans, work boots. He works a "
    "pneumatic framing nail gun fed by a hose from the orange compressor, with two collated nail "
    "racks (strips of nails in plastic sheaths) and the metal bucket. "
)

WINSLADE = (
    "WINSLADE — lean, sharp-featured officer in his 40s, slicked dark hair, smug precise expression. "
    "He wears a Tribune's uniform from the Undying Mercenaries legions: a dark navy-black smart-cloth "
    "tunic cinched tight, high collar, subtle single-star Tribune rank insignia at the collar, fitted "
    "trousers and boots — no hard hat, no hi-vis. On his forearm is his TAPPER: a bio-grown computer "
    "whose glowing touchscreen shows just under the skin of his inner forearm, which he raises, taps "
    "and checks like a wrist device. "
)

YESHUA = (
    "YESHUA — a quiet carpenter in his 30s, normal human body, work shirt, tool belt and boots. "
    "His FACE is not a human face and not an animal: it is a CAT-SHAPED form — pointed feline ears, "
    "broad feline cheek planes, a cat's silhouette — and inside that cat shape is COSMOS: deep "
    "starfield, nebulae and tiny sharp stars filling the whole face, no fur, no whiskers, no cat eyes, "
    "no mask. The universe in the shape of a cat's face, calm and present. "
)

REF_PROMPTS: dict[str, str] = {
    "stamper": STAMPER + "Full-body character reference plate, standing three-quarter view, plain warm-grey studio background, neutral expression. " + STYLE,
    "happy": HAPPY + "Full-body character reference plate, standing three-quarter view holding the nail gun down at his side, plain warm-grey studio background. " + STYLE,
    "winslade": WINSLADE + "Full-body character reference plate, standing three-quarter view, one forearm raised checking the glowing tapper under his skin, plain warm-grey studio background. " + STYLE,
    "yeshua": YESHUA + "Full-body character reference plate, standing three-quarter view, hands empty and relaxed, plain warm-grey studio background. " + STYLE,
    "site": SITE + "Wide establishing plate of the empty site, no people. " + STYLE,
}

# id, first cue, last cue, refs, scene
SLIDES: list[tuple[str, int, int, tuple[str, ...], str]] = [
    ("01_sign", 480, 480, (), "THE TUROV SIGN — handled by reusing the existing composed sign plate."),
    ("02_introductions", 481, 483, ("stamper", "happy", "winslade", "site"),
     "Wide group introduction on the slab: Stamper in his grey EVA suit holding his clipboard, Happy by the compressor with his nail gun and two nail racks, Winslade apart checking his glowing forearm tapper. All three look toward the viewer. "),
    ("03_vincent_coin", 484, 484, ("vincent", "site"),
     "Vincent stands at the edge of the slab reciting from memory, calm, one hand in his pocket, checking nothing. The crew's equipment is around him; he is the only still figure. "),
    ("04_rack_pull", 485, 487, ("happy", "site"),
     "Close working shot: Happy pulls the first collated nail rack out of the nail gun, holds it level, and pulls one nail cleanly through its sheath by the head, dropping it into the bucket. Second rack still in the gun. "),
    ("05_rack_swap", 488, 488, ("happy", "site"),
     "Happy holds the two nail racks up parallel at eye level, counting sheath by sheath against each other, about to swap their order in the gun. Bucket with two nails below. "),
    ("06_chalk_snore", 489, 490, ("happy", "site"),
     "Happy kneels to make one chalk tally mark on the concrete, then sits back with eyes closed in one theatrical snore, nail gun resting across his knees. "),
    ("07_bleed_reset", 491, 492, ("happy", "site"),
     "Happy unhooks the hose from the nail gun and bleeds the air line open beside the orange compressor, then reconnects it as the compressor comes back up to pressure, gauge visible. "),
    ("08_happy_motion", 493, 494, ("happy", "site"),
     "Happy performs one brief absurd athletic flourish with the nail gun — a hockey slapshot / golf swing hybrid motion, deadly serious face — then resets to start the cycle again. "),
    ("09_walkthrough", 495, 499, ("winslade", "stamper", "happy", "site"),
     "Winslade steps in raising his tapper forearm, demanding a walkthrough; Stamper beside him in the grey EVA suit says he needs to see it from the beginning; Happy, gun in hand, protests that he just did it. "),
    ("10_redo", 500, 503, ("happy", "winslade", "site"),
     "Happy does the whole cycle again under inspection: rack out, one nail from its sheath into the bucket, rack slid back — while Winslade watches his glowing tapper, timing him. "),
    ("11_gun_question_ghost_spec", 504, 512, ("winslade", "stamper", "happy", "site"),
     "Winslade points at the nail gun asking about the flourish at the end and whether it is in the spec. Behind him Stamper stares intently at an invisible document held in his empty hands — clipboard tucked under his arm — reading what is not there. "),
    ("12_steps_file_offset", 513, 529, ("stamper", "happy", "winslade", "site"),
     "Stamper teaches the procedure like a spec: pointing from the nail racks to the bucket to chalk tallies, explaining head positions and file offsets. Happy answers while working; Winslade asks what a file offset is, tapper glowing. "),
    ("13_bucket_two_nails", 530, 532, ("winslade", "stamper", "site"),
     "Low close shot: the metal bucket on the concrete containing exactly two loose nails. Winslade leans over it, tapper forearm lit, while Stamper's grey-suited legs and clipboard stand beside him. Two cycles. "),
    ("14_rotation_presence", 533, 544, ("stamper", "happy", "winslade", "site"),
     "Stamper draws a thirty-degree rotation arc in chalk on the slab and gestures the swap of the two racks, explaining presence checks and the skip list. Happy holds both racks, listening; Winslade records on his tapper. "),
    ("15_step_seven_confirmed", 545, 547, ("stamper", "winslade", "happy", "site"),
     "Stamper gives one confirming nod over his clipboard — step seven confirmed. Winslade lowers his tapper. Happy is already reaching for the first rack to start again. "),
    ("16_rack_runs_out", 548, 555, ("winslade", "stamper", "happy", "site"),
     "Winslade and Stamper peer down at the two nail racks lying on the concrete, trying and failing to tell whether they hold the same number of nails. Happy shrugs: not his responsibility to keep track of. "),
    ("17_yeshua_needs_nails", 556, 562, ("yeshua", "happy", "winslade", "site"),
     "A carpenter walks onto the slab — Yeshua, his cat-shaped face filled with cosmos and stars — and gestures at the bucket of loose nails: he needs them to do his job. Happy hands the bucket over easily. Winslade steps in, alarmed, raising his tapper. "),
    ("18_operational_deficiency", 563, 579, ("yeshua", "winslade", "stamper", "happy", "site"),
     "Happy returns with two fresh nail racks and an empty bucket and sets them exactly where the old ones were. Winslade flags the carpenter's request on his glowing tapper as an operational deficiency while Stamper argues operations continued with little impedance. Yeshua stands to one side, cosmos-cat face calm, holding his nails. "),
    ("19_emmet_foreman", 580, 584, ("stamper", "happy", "winslade", "site"),
     "On a crate at the edge of the slab stands the site foreman: a small cheerful LEGO minifigurine with a clipboard, radiating relentless optimism. The three men regard him — Winslade approving, Happy bored, Stamper faintly annoyed by unbounded cheer. "),
    ("20_binary_wouldnt_show", 585, 592, ("happy", "stamper", "winslade", "site"),
     "Happy unplugs the hose and bleeds the line again while Stamper explains, chalk in hand: one nail per cycle, each nail one address rotated, the sheaths holding the order. A coin flip would tell you nothing about the thirty degrees. "),
    ("21_coins_offered", 593, 603, ("happy", "winslade", "stamper", "site"),
     "Happy holds out two coins in his open palm — one copper penny, one silver nickel — offering a choice. Winslade reaches for the nickel; Stamper, the asteroid miner, takes the penny: the ore is more valuable than the coin. "),
    ("22_coin_flip_spinning", 604, 615, ("stamper", "winslade", "happy", "site"),
     "Two coins spin in the air above the slab, caught mid-flip as blurred copper and silver spheres — neither heads nor tails, both faces at once. Below, Stamper has opened his clipboard to a blank page and is writing annotations; the compressor roars back on. "),
    ("23_step_eight_mark", 616, 633, ("happy", "winslade", "stamper", "site"),
     "Close on the concrete: Happy makes another chalk mark, a small tally in the corner with figures written on it. Winslade crouches to read the mark, tapper glowing; Stamper watches. Different iteration, same place. "),
    ("24_mark_not_cycle", 634, 643, ("stamper", "happy", "winslade", "site"),
     "Stamper stands very still, thinking, then explains with two flat hands at different heights: the mark is not the cycle — the cycle already happened; the mark is the log that a log has been recorded. Happy demonstrates that processes and daemons are not the same thing. "),
    ("25_skip_mark_never_happened", 644, 653, ("happy", "stamper", "winslade", "site"),
     "Happy deliberately skips the mark: unplugs the hose, kills the compressor, bleeds the line, makes no chalk mark at all, restarts. The three men stare at the unmarked concrete where a tally should be. It never happened. "),
    ("26_step_nine_proof", 654, 666, ("happy", "stamper", "winslade", "site"),
     "Happy pulls a single nail from its sheath and tosses it into the bucket. Stamper points from the fresh mark to the bucket: step nine — the mark is the proof of absence of failure. Happy nods, mild, as a person nods when a true thing is correctly stated. "),
    ("27_approved_raise_game", 667, 676, ("winslade", "happy", "stamper", "site"),
     "Winslade taps his tapper once and lets it close: the work is approved, the raise is approved, and the night off for the Bruins game — denied before — is approved now. Happy does not look as happy as expected; he looks at the chalk in his hand. "),
    ("28_final_coins_flat", 677, 687, ("happy", "stamper", "winslade", "site"),
     "End of day on the slab. The compressor still runs. Chalk marks cover one corner of the concrete; nails sit in the bucket; on a flat surface lie the two coins, both face-up, one of them heads. Winslade's tapper has gone dark. Nobody disagrees with anything. Warm last light. "),
]


def api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY for --render")
    return key


def generate(sid: str, prompt: str, dest: Path, size: str, *, force: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not force and dest.exists() and dest.stat().st_size > 8000:
        print(f"  [skip] {sid}")
        return
    import requests

    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
        json={"model": "gpt-image-1.5", "prompt": prompt, "size": size,
              "quality": "high", "output_format": "png", "n": 1},
        timeout=300,
    )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code}: {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid} ({dest.stat().st_size // 1024} KB)")


def edit_with_refs(sid: str, prompt: str, ref_paths: list[Path], dest: Path, *, force: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.with_suffix(".request.json").write_text(json.dumps(
        {"id": sid, "refs": [str(p) for p in ref_paths], "prompt": prompt}, indent=2) + "\n")
    if not force and dest.exists() and dest.stat().st_size > 8000:
        print(f"  [skip] {sid}")
        return
    import requests

    handles = [open(p, "rb") for p in ref_paths]
    try:
        files = [("image[]", (p.name, h, "image/png")) for p, h in zip(ref_paths, handles)]
        r = requests.post(
            "https://api.openai.com/v1/images/edits",
            headers={"Authorization": f"Bearer {api_key()}"},
            files=files,
            data={"model": "gpt-image-1.5", "prompt": prompt, "size": "1536x1024",
                  "quality": "high", "output_format": "png", "n": "1"},
            timeout=300,
        )
    finally:
        for h in handles:
            h.close()
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code}: {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid} ({dest.stat().st_size // 1024} KB)")


def ref_for(name: str) -> Path:
    if name == "vincent":
        return VINCENT_REF
    return REFS / f"{name}.png"


def cmd_refs(render: bool = False, force: bool = False) -> None:
    REFS.mkdir(parents=True, exist_ok=True)
    for sid, prompt in REF_PROMPTS.items():
        dest = REFS / f"{sid}.png"
        if render:
            generate(sid, prompt, dest, "1024x1536" if sid != "site" else "1536x1024", force=force)
        else:
            print(f"  [dry] ref {sid}")


def cmd_stills(render: bool = False, force: bool = False) -> None:
    STILLS.mkdir(parents=True, exist_ok=True)
    cmd_refs(render=render, force=False)
    for sid, _a, _b, refs, scene in SLIDES:
        dest = STILLS / f"{sid}.png"
        if sid == "01_sign":
            if not SIGN_GOOD.exists():
                sys.exit(f"missing good sign plate {SIGN_GOOD}")
            if force or not dest.exists():
                import shutil
                shutil.copy2(SIGN_GOOD, dest)
                print("  [ok] 01_sign (reused composed TUROV sign plate)")
            else:
                print("  [skip] 01_sign")
            continue
        bible = "\n".join(x for x in (VINCENT, STAMPER, HAPPY, WINSLADE, YESHUA)
                          if any(r in x.lower() for r in refs))
        prompt = (STYLE + SITE + bible + "\nSCENE: " + scene +
                  "Keep the exact same faces, hair, costumes and site layout as the reference images. "
                  "Wide 16:9 cinematic framing, characters fully in frame. "
                  "Absolutely NO speech bubbles, NO dialogue balloons, NO captions, NO words anywhere.")
        if render:
            paths = [ref_for(r) for r in refs]
            missing = [str(p) for p in paths if not p.exists()]
            if missing:
                sys.exit(f"missing refs {missing} — run refs --render")
            edit_with_refs(sid, prompt, paths, dest, force=force)
        else:
            print(f"  [dry] {sid} refs={refs}")


def load_cues() -> list[dict]:
    p = AUDIO_MAIN / "cues.jsonl"
    if not p.exists():
        sys.exit(f"Missing {p}")
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def sign_goat_segments() -> list[dict]:
    """Goat reads the posted TUROV advisory verbatim — headers, body, closing line."""
    sys.path.insert(0, str(BASE / "tools"))
    import compose_turov_sign as cts
    import generate_audio as ga

    h1, h2, words = cts.load_turov_words()
    body = ga.clean_text(" ".join(words))
    out: list[dict] = [{
        "key": "sign_0",
        "speaker": "Goat",
        "text": ga.clean_text(f"{h1}. {h2}."),
    }]
    for i, chunk in enumerate(ga.chunk_text(body, limit=1800), start=1):
        out.append({"key": f"sign_{i}", "speaker": "Goat", "text": chunk})
    out.append({
        "key": "sign_end",
        "speaker": "Goat",
        "text": "END OF ADVISORY ADVISORY.",
    })
    return out


def clip_segments() -> list[dict]:
    """Goat opens on the sign; then scene from -09 with GoinesFeynman narration.

    The Narrator is not the narrator for this scene. All italic/stage lines
    go to GoinesFeynman (haunt voice). Dialogue keeps its original cast.
    The Man (Yeshua) is dropped by the -09 parser's cast list; his two
    lines are restored here in the Yeshua Merlin register.
    """
    sys.path.insert(0, str(BASE / "tools"))
    import build_lisbeth_audio as lb

    out: list[dict] = list(sign_goat_segments())
    segs = lb.parse_minus09()
    start = next(i for i, (_s, t) in enumerate(segs)
                 if t.startswith("The Narrator would like to introduce"))
    for orig_i, (speaker, text) in enumerate(segs[start:], start=start):
        out.append({"key": orig_i, "speaker": speaker, "text": text})
        if text.startswith("A man comes by."):
            out.append({"key": "man1", "speaker": "Yeshua Merlin",
                        "text": "Can I take those nails?"})
        if text == "Wait. Why do you need them?":
            out.append({"key": "man2", "speaker": "Yeshua Merlin",
                        "text": "I need them to do my job."})
    for seg in out:
        if seg["speaker"] == "The Narrator":
            seg["speaker"] = "GoinesFeynman"
    return out


def cmd_audio() -> None:
    """Synthesise the clip audio fresh (GoinesFeynman narration).

    Dialogue reuses the ElevenLabs hash cache from the -09 build; only the
    re-cast narration and the restored Yeshua lines are new calls.
    """
    sys.path.insert(0, str(BASE / "tools"))
    import build_lisbeth_audio as lb
    import generate_audio as ga

    CLIP.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    cues: list[dict] = []
    t = 0.0
    for seg in clip_segments():
        speaker = seg["speaker"]
        text = ga.clean_text(seg["text"])
        vid = ga.VOICE_MAP.get(speaker)
        if not vid:
            sys.exit(f"no voice for {speaker}")
        # Goat reads the sign: flash_v2 supports CMU <phoneme> for Gattaca (ga·tuh·kuh).
        model_id = "eleven_flash_v2" if speaker == "Goat" else "eleven_multilingual_v2"
        files = ga.tts(speaker, text, vid, model_id=model_id, language_code="en")
        for p in files:
            d = lb.ffprobe_dur(p)
            paths.append(p)
            cues.append({"key": seg["key"], "start": round(t, 4),
                         "end": round(t + d, 4), "dur": round(d, 4),
                         "speaker": speaker, "text": text})
            t += d
    if not ga.concatenate(paths, AUDIO_CLIP):
        sys.exit("audio concat failed")
    (CLIP / "clip_cues.jsonl").write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues))
    n_goat = sum(1 for c in cues if c["speaker"] == "Goat")
    print(f"Audio clip → {AUDIO_CLIP} ({t:.1f}s, {len(cues)} cues, sign=Goat×{n_goat})")


def cmd_assemble() -> None:
    if not AUDIO_CLIP.exists() or not (CLIP / "clip_cues.jsonl").exists():
        cmd_audio()
    cues = [json.loads(l) for l in (CLIP / "clip_cues.jsonl").read_text().splitlines() if l]
    pos = {c["key"]: c for c in cues}
    sign_cues = [c for c in cues if str(c["key"]).startswith("sign")]
    lines = ["ffconcat version 1.0"]
    total = 0.0
    last = None
    for n, (sid, a, b, _refs, _scene) in enumerate(SLIDES):
        p = STILLS / f"{sid}.png"
        if not p.exists():
            sys.exit(f"missing slide {p} — run stills --render")
        if n == 0 and sign_cues:
            goat_dur = max(c["end"] for c in sign_cues) - min(c["start"] for c in sign_cues)
            dur = max(0.5, SIGN_HOLD + goat_dur)
        else:
            dur = max(0.5, float(pos[b]["end"]) - float(pos[a]["start"]))
        total += dur
        lines += [f"file '{p}'", f"duration {dur:.4f}"]
        last = p
    lines.append(f"file '{last}'")
    concat = CLIP / "concat_real.txt"
    concat.write_text("\n".join(lines) + "\n")
    final = OUT / "-09_turov_nailgun_review.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-itsoffset", f"{SIGN_HOLD}", "-i", str(AUDIO_CLIP),
         # No fps filter: it silently eats the first slide (the sign).
         # The concat stream already carries one frame per image with its
         # duration; vsync duplicates them cheaply under stillimage tune.
         "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=yuv420p",
         "-c:v", "libx264", "-tune", "stillimage", "-crf", "19", "-g", "125", "-bf", "0",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)],
        check=True)
    print(f"Slideshow {total:.1f}s, {len(SLIDES)} images → {final} ({final.stat().st_size // 1024 // 1024} MB)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["audio", "refs", "stills", "assemble", "all"])
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if args.cmd == "audio":
        cmd_audio()
    elif args.cmd == "refs":
        cmd_refs(render=args.render, force=args.force)
    elif args.cmd == "stills":
        cmd_stills(render=args.render, force=args.force)
    elif args.cmd == "assemble":
        cmd_assemble()
    elif args.cmd == "all":
        cmd_audio()
        cmd_stills(render=args.render, force=args.force)
        cmd_assemble()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Consistency patch: Sauron speaks which/witch tallies through the palantir.

- which_*.json: deliverer=SAURON; section speakers → SAURON; studio frame kept
  but labeled as flinch, not 'who reads'
- Re-inject which HTML into episode_*.html via gen_which_sections._section_block

Does not call the API. Does not rewrite film audio (reassemble separately if needed).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EP_DIR = ROOT / "prompt_walk_page_builder" / "episodes"
sys.path.insert(0, str(ROOT / "prompt_walk_page_builder"))
from gen_which_sections import WHICH_CSS, _section_block  # noqa: E402

CECIL_FRAME_PREFIXES = (
    "proceeding under duress",
    "well, sauron has sent",
    "i'm just reading through",
    "i would rather not",
    "it’s sauron’s section",
    "it's sauron’s section",
    "it's sauron's section",
)


def patch_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["deliverer"] = "SAURON"
    data["episode"] = data.get("episode") or int(re.search(r"(\d+)", path.stem).group(1))

    # Soften debate into studio frame if it still argues who must read.
    debate = data.get("debate") or []
    reframed = []
    for turn in debate:
        line = turn.get("line", "")
        low = line.lower()
        if "who has to" in low or "you take it" in low or "i'll do it" in low or "i will do it" in low:
            # keep as comic flinch but don't resolve to human delivery
            reframed.append(turn)
        else:
            reframed.append(turn)
    if reframed:
        # Append a closing beat that hands the mic to the stone if missing.
        last = " ".join(t.get("line", "").lower() for t in reframed[-2:])
        if "palantir" not in last and "stone" not in last and "eye" not in last:
            reframed.append(
                {
                    "speaker": "NARRATOR",
                    "line": "The palantir is already warm. He does not require a lector.",
                }
            )
            reframed.append(
                {
                    "speaker": "CECIL",
                    "line": "Right. Of course. The Eye speaks. We… listen. Professionally.",
                }
            )
    data["debate"] = reframed

    section = []
    for ln in data.get("section") or []:
        text = ln.get("line", "")
        low = text.lower().strip()
        # Drop overt "I am reading Sauron's account" openers from former deliverers.
        if any(low.startswith(p) for p in CECIL_FRAME_PREFIXES):
            continue
        if low.startswith("five uses of 'which'") or low.startswith("three instances of 'which'"):
            # already analysis — attribute to Sauron
            section.append({"speaker": "SAURON", "line": text})
            continue
        section.append({"speaker": "SAURON", "line": text})
    if not section:
        section = [{"speaker": "SAURON", "line": "(tally body missing after patch)"}]
    data["section"] = section

    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def patch_html(ep_n: int, section: dict) -> None:
    ep_html = EP_DIR / f"episode_{ep_n:02d}.html"
    if not ep_html.exists():
        return
    text = ep_html.read_text(encoding="utf-8")
    # Strip prior which-section blocks
    text = re.sub(
        r"<section class='which-section'>.*?</section>\s*",
        "",
        text,
        flags=re.S,
    )
    if ".which-section" not in text:
        text = text.replace("</style>", WHICH_CSS + "\n</style>")
    block = _section_block(section)
    if "</body>" in text:
        text = text.replace("</body>", block + "\n</body>")
    else:
        text = text + block
    ep_html.write_text(text, encoding="utf-8")


def main() -> None:
    for path in sorted(EP_DIR.glob("which_*.json")):
        section = patch_json(path)
        ep_n = int(section["episode"])
        patch_html(ep_n, section)
        print(f"✓ {path.name} → SAURON / palantir; episode_{ep_n:02d}.html injected")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Assemble reviewer desks: one endpoint per manuscript, same tree a
journal would receive. Static files + files.json. No mock URLs.

  .venv/bin/python tools/build_desks.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
WEB = BASE / "web"
PKG = (
    BASE
    / "manuscripts"
    / "how_to_fly_ajp"
    / "package"
    / "how_to_fly_aerodynamic_plefr_submission_package"
)
COVER = BASE / "manuscripts" / "how_to_fly_ajp" / "Cover_Letter_HOW_TO_FLY.md"
MANIFESTO = (
    Path("/home/dylanmccapes/dev/docs/glacial_cell_sim/results")
    / "MANIFESTO_MOTHER_EARTH_GOVERNED_FIELD.pdf"
)
BOOK = BASE / "REALITY_USER_MANUAL.pdf"
PLOS = (
    Path("/home/dylanmccapes/dev/PORTAL_VISION_LUCIFER/distributions")
    / "plos_plume_wave_intracellular_transport"
)


def copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        print(f"  [missing] {src}")
        return
    shutil.copy2(src, dest)
    print(f"  {dest.relative_to(WEB)}")


def kind(name: str) -> str:
    suf = Path(name).suffix.lower()
    if suf == ".pdf":
        return "pdf"
    if suf in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return "image"
    return "text"


def tree_from(dirpath: Path, url_prefix: str) -> list[dict]:
    nodes = []
    if not dirpath.exists():
        return nodes
    for p in sorted(dirpath.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if p.name.startswith("."):
            continue
        if p.is_dir():
            nodes.append({
                "name": p.name,
                "type": "dir",
                "children": tree_from(p, f"{url_prefix}/{p.name}"),
            })
        else:
            nodes.append({
                "name": p.name,
                "type": kind(p.name),
                "url": f"{url_prefix}/{p.name}",
                "bytes": p.stat().st_size,
            })
    return nodes


def write_files_json(desk: Path, meta: dict, files_dir: Path,
                     extra: list[dict] | None = None) -> None:
    payload = dict(meta)
    payload["tree"] = tree_from(files_dir, "files") + list(extra or [])
    dest = desk / "files.json"
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"  {dest.relative_to(WEB)}")


def write_desk_page(desk: Path) -> None:
    src = WEB / "desk.html"
    shutil.copy2(src, desk / "index.html")


def how_to_fly() -> None:
    desk = WEB / "m" / "how-to-fly"
    files = desk / "files"
    if files.exists():
        shutil.rmtree(files)
    pairs = [
        (COVER, files / "INTAKE" / "Cover_Letter_HOW_TO_FLY.md"),
        (PKG / "README_SUBMISSION_PACKAGE.md", files / "INTAKE" / "README_SUBMISSION_PACKAGE.md"),
        (PKG / "JOURNAL_TARGET_RECOMMENDATION.md", files / "INTAKE" / "JOURNAL_TARGET_RECOMMENDATION.md"),
        (PKG / "Main_Manuscript_HOW_TO_FLY.pdf", files / "SEQUENCE" / "Main_Manuscript_HOW_TO_FLY.pdf"),
        (PKG / "Main_Manuscript_HOW_TO_FLY.md", files / "SEQUENCE" / "Main_Manuscript_HOW_TO_FLY.md"),
        (PKG / "Supporting_Information_HOW_TO_FLY.pdf", files / "ASSAY" / "Supporting_Information_HOW_TO_FLY.pdf"),
        (PKG / "Supporting_Information_HOW_TO_FLY.md", files / "ASSAY" / "Supporting_Information_HOW_TO_FLY.md"),
        (PKG / "Source" / "HOW_TO_FLY.md", files / "LINEAGE" / "HOW_TO_FLY.md"),
        (PKG / "Supplementary" / "OPERATOR_SEED_HOW_TO_FLY.pdf", files / "SUPPLEMENT" / "OPERATOR_SEED_HOW_TO_FLY.pdf"),
        (PKG / "Supplementary" / "HIERARCHICAL_VISUAL_MAP_HOW_TO_FLY_20260228.md", files / "SUPPLEMENT" / "HIERARCHICAL_VISUAL_MAP_HOW_TO_FLY_20260228.md"),
    ]
    figs = PKG / "Figures"
    if figs.exists():
        for p in sorted(figs.glob("*.png")):
            pairs.append((p, files / "PLATES" / p.name))
    for src, dest in pairs:
        copy(src, dest)
    write_files_json(desk, {
        "id": "how-to-fly",
        "title": "How to Fly: Pressure Gradients, PLEFR Fields, and Lift Regime Physics",
        "author": "Dylan McCapes",
        "target": "American Journal of Physics",
        "received": "2026-03-01",
        "station": "how-to-fly",
        "note": "Gattaca intake tree. Reviewer files only. No receipts, no FullMetalPacket.",
        "open": "files/SEQUENCE/Main_Manuscript_HOW_TO_FLY.pdf",
    }, files)
    write_desk_page(desk)


def glacial() -> None:
    desk = WEB / "m" / "glacial-cell"
    files = desk / "files"
    if files.exists():
        shutil.rmtree(files)
    copy(MANIFESTO, files / "SEQUENCE" / "MANIFESTO_MOTHER_EARTH_GOVERNED_FIELD.pdf")
    write_files_json(desk, {
        "id": "glacial-cell",
        "title": "Mother Earth as Governed Field",
        "author": "Dylan McCapes",
        "target": "first true manuscript — manifesto, not a journal coat",
        "received": "2026-10-22",
        "station": "glacial-cell",
        "note": "Gattaca intake. Sequence only: the manifesto.",
        "open": "files/SEQUENCE/MANIFESTO_MOTHER_EARTH_GOVERNED_FIELD.pdf",
    }, files)
    write_desk_page(desk)


def plume_wave() -> None:
    """PLOS Computational Biology package: plume-wave intracellular transport.
    theory_vision.jsonl status DOCUMENTED; ACS fallback track (2026-02-27)."""
    desk = WEB / "m" / "plume-wave"
    files = desk / "files"
    if files.exists():
        shutil.rmtree(files)
    pairs = [
        (PLOS / "Cover_Letter_PLOS.pdf", files / "INTAKE" / "Cover_Letter_PLOS.pdf"),
        (PLOS / "Cover_Letter_PLOS.md", files / "INTAKE" / "Cover_Letter_PLOS.md"),
        (PLOS / "README_SUBMISSION_PACKAGE.md", files / "INTAKE" / "README_SUBMISSION_PACKAGE.md"),
        (PLOS / "Publication_Fee_Assistance_Supporting_Statement.pdf", files / "INTAKE" / "Publication_Fee_Assistance_Supporting_Statement.pdf"),
        (PLOS / "Main_Manuscript_Plume_Wave_Intracellular_Transport.pdf", files / "SEQUENCE" / "Main_Manuscript_Plume_Wave_Intracellular_Transport.pdf"),
        (PLOS / "Main_Manuscript_Plume_Wave_Intracellular_Transport.md", files / "SEQUENCE" / "Main_Manuscript_Plume_Wave_Intracellular_Transport.md"),
        (PLOS / "Supporting_Information.pdf", files / "ASSAY" / "Supporting_Information.pdf"),
        (PLOS / "Supporting_Information.md", files / "ASSAY" / "Supporting_Information.md"),
        (PLOS / "01_SOURCE_THEORY_PLUME_WAVE_ROUTING_BIOLOGICAL_SYSTEMS.md", files / "LINEAGE" / "01_SOURCE_THEORY_PLUME_WAVE_ROUTING_BIOLOGICAL_SYSTEMS.md"),
        (PLOS / "02_SUPPORTING_INTRACELLULAR_TRAFFIC_JAM_RECEIPT.md", files / "LINEAGE" / "02_SUPPORTING_INTRACELLULAR_TRAFFIC_JAM_RECEIPT.md"),
    ]
    supp = PLOS / "Supplementary"
    for p in sorted(supp.glob("Supplementary_P*.pdf")):
        pairs.append((p, files / "SUPPLEMENT" / p.name))
    for p in sorted(supp.glob("sim_p*.py")):
        pairs.append((p, files / "SUPPLEMENT" / p.name))
    for p in sorted(supp.glob("*.png")):
        pairs.append((p, files / "PLATES" / p.name))
    for src, dest in pairs:
        copy(src, dest)
    write_files_json(desk, {
        "id": "plume-wave",
        "title": "Plume-Wave Routing in Intracellular Transport",
        "author": "Dylan McCapes",
        "target": "PLOS Computational Biology",
        "received": "2026-03-09",
        "station": "plume-wave",
        "note": "Gattaca intake tree. Four simulations (P1–P4), four predictions. ACS fallback track.",
        "open": "files/SEQUENCE/Main_Manuscript_Plume_Wave_Intracellular_Transport.pdf",
    }, files)
    write_desk_page(desk)


def how_tos() -> None:
    """The 22 HOW_TOs as one searchable page. tools/build_how_tos.py writes
    the HTML; this just makes sure it is there."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_how_tos", Path(__file__).with_name("build_how_tos.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.main()
    print(f"  {out.relative_to(WEB)}")


# The book's desk lists the other stations under DISTRIBUTIONS. Hand-kept
# here so a rebuild does not drop them.
DISTRIBUTIONS = [
    {
        "name": "HOW_TO stack (22 documents, searchable)",
        "type": "html",
        "url": "/m/how-tos/",
        "label": "page −09",
    },
    {
        "name": "How to Fly",
        "type": "pdf",
        "url": "/m/how-to-fly/files/SEQUENCE/Main_Manuscript_HOW_TO_FLY.pdf",
        "label": "AJP submission",
    },
    {
        "name": "Mother Earth as Governed Field",
        "type": "pdf",
        "url": "/m/glacial-cell/files/SEQUENCE/MANIFESTO_MOTHER_EARTH_GOVERNED_FIELD.pdf",
        "label": "first true manuscript",
    },
    {
        "name": "Plume-Wave Routing in Intracellular Transport",
        "type": "pdf",
        "url": "/m/plume-wave/files/SEQUENCE/Main_Manuscript_Plume_Wave_Intracellular_Transport.pdf",
        "label": "PLOS Comp Bio submission",
    },
]


def book() -> None:
    desk = WEB / "m" / "reality-user-manual"
    files = desk / "files"
    if files.exists():
        shutil.rmtree(files)
    copy(BOOK, files / "SEQUENCE" / "REALITY_USER_MANUAL.pdf")
    write_files_json(desk, {
        "id": "reality-user-manual",
        "title": "REALITY_USER_MANUAL",
        "author": "Dylan McCapes",
        "target": "the book",
        "received": "2026-10-25",
        "station": "reality-user-manual",
        "note": "Gattaca intake. The bound volume is the sequence.",
        "open": "files/SEQUENCE/REALITY_USER_MANUAL.pdf",
    }, files, extra=[{"name": "DISTRIBUTIONS", "type": "dir", "children": DISTRIBUTIONS}])
    write_desk_page(desk)


def inbox() -> None:
    (WEB / "manuscripts.json").write_text(json.dumps({
        "site": "https://realityusermanual.dylanmccapes.systems",
        "manuscripts": [
            {
                "id": "how-to-fly",
                "href": "/m/how-to-fly/",
                "title": "How to Fly",
                "target": "American Journal of Physics",
            },
            {
                "id": "glacial-cell",
                "href": "/m/glacial-cell/",
                "title": "Mother Earth as Governed Field",
                "target": "first true manuscript",
            },
            {
                "id": "plume-wave",
                "href": "/m/plume-wave/",
                "title": "Plume-Wave Routing in Intracellular Transport",
                "target": "PLOS Computational Biology",
            },
            {
                "id": "how-tos",
                "href": "/m/how-tos/",
                "title": "HOW_TO stack",
                "target": "22 documents, one page, searchable",
            },
            {
                "id": "reality-user-manual",
                "href": "/m/reality-user-manual/",
                "title": "REALITY_USER_MANUAL",
                "target": "the book",
            },
        ],
    }, indent=2) + "\n")


def main() -> None:
    WEB.mkdir(parents=True, exist_ok=True)
    if not (WEB / "desk.html").exists():
        raise SystemExit("web/desk.html missing")
    how_to_fly()
    glacial()
    plume_wave()
    how_tos()
    book()
    inbox()
    print(f"desks at {WEB}")


if __name__ == "__main__":
    main()

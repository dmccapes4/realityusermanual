"""imessage_thread v0.0.5 pipeline — stages 0..8 (see GAME_PLAN_v0.0.5.md)."""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any

from attribute_vision import attribute_frame
from contact import extract_contact
from crop import crop_thread, load_profile
from format_report import fill_report, format_transcript_md, scaffold_report
from gpt41_pass import run_gpt41_pass
from io_jsonl import read_jsonl, write_json_atomic, write_jsonl_atomic
from ocr import ENGINE, ensure_tesseract, extract_thread_markers, ocr_confidence, ocr_image
from report_model import run_report
from thread_tools import frame_geometry, messages_from_attributed, messages_from_transcript_rows, prestitch, to_transcript_rows

STAGES = ["init", "contact", "crop", "ocr", "attribute", "stitch", "review", "scaffold", "report"]
TOOL_DIR = Path(__file__).resolve().parent
VERSION = (TOOL_DIR / "VERSION").read_text(encoding="utf-8").strip()


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")


def _natural_key(p: Path) -> list:
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", p.name)]


def list_images(images_dir: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted((p.resolve() for p in images_dir.iterdir() if p.suffix.lower() in exts), key=_natural_key)


def new_run_id(slug: str) -> str:
    ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug).strip("_") or "thread"
    return f"{safe}_{ts}"


class Run:
    def __init__(self, run_dir: Path):
        self.dir = run_dir
        self.meta_path = run_dir / "run_meta.json"
        self.contact_path = run_dir / "contact.json"
        self.ocr_path = run_dir / "ocr.jsonl"
        self.attributed_path = run_dir / "attributed.jsonl"
        self.transcript_path = run_dir / "transcript.jsonl"
        self.pass1_path = run_dir / "gpt41_pass1.json"
        self.pass2_path = run_dir / "gpt41_pass2.json"
        self.report_path = run_dir / "report.md"
        self.log_path = run_dir / "run.log"
        self.crops_dir = run_dir / "crops"

    def log(self, msg: str) -> None:
        line = f"{_now()} {msg}"
        print(line)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def meta(self) -> dict[str, Any]:
        return json.loads(self.meta_path.read_text(encoding="utf-8")) if self.meta_path.is_file() else {}

    def save_meta(self, meta: dict[str, Any]) -> None:
        write_json_atomic(self.meta_path, meta)

    def contact(self) -> dict[str, Any]:
        return json.loads(self.contact_path.read_text(encoding="utf-8")) if self.contact_path.is_file() else {}

    def frames(self) -> list[dict[str, Any]]:
        return read_jsonl(self.ocr_path)


# ----------------------------------------------------------------------------- stages


def stage_init(run: Run, *, run_id: str, images: list[Path], images_dir: Path, process_date: str, tz: str, models: dict[str, str], profile_path: Path) -> None:
    run.dir.mkdir(parents=True, exist_ok=True)
    run.crops_dir.mkdir(exist_ok=True)
    for p in (run.ocr_path, run.attributed_path, run.transcript_path, run.report_path, run.log_path):
        if not p.exists():
            p.write_text("", encoding="utf-8")
    for p in (run.contact_path, run.pass1_path, run.pass2_path):
        if not p.exists():
            p.write_text("{}\n", encoding="utf-8")
    meta = {
        "run_id": run_id,
        "version": VERSION,
        "created_at": _now(),
        "images_dir": str(images_dir),
        "image_count": len(images),
        "images": [p.name for p in images],
        "capture_assumption_date": process_date,
        "processing_timezone": tz,
        "crop_profile": str(profile_path),
        "models": models,
        "assumptions": {
            "0a": "single_contact_imessage_thread",
            "0b": "screenshots_taken_on_process_date",
            "0c": "image_order_is_thread_order",
        },
    }
    run.save_meta(meta)
    run.log(f"init run_dir={run.dir} images={len(images)} version={VERSION}")


def stage_contact(run: Run, *, images: list[Path], profile: dict[str, Any], model_mini: str, process_date: str, tz: str) -> dict[str, Any]:
    ensure_tesseract()
    contact = extract_contact(images[0], profile, model_fallback=model_mini, process_date=process_date, tz=tz)
    write_json_atomic(run.contact_path, contact)
    meta = run.meta()
    meta["contact_name"] = contact.get("contact_name")
    meta["contact_slug"] = contact.get("contact_slug")
    meta["thread_anchor"] = contact.get("thread_anchor")
    meta["contact_committed_at"] = _now()
    run.save_meta(meta)
    run.log(f"contact name={contact.get('contact_name')} slug={contact.get('contact_slug')} locality={contact.get('contact_locality')} anchor={(contact.get('thread_anchor') or {}).get('raw')} via={contact.get('contact_source')}")
    return contact


def stage_crop(run: Run, *, images: list[Path], profile: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, p in enumerate(images):
        img, mode, box, note = crop_thread(p, profile)
        out = run.crops_dir / f"{p.stem}.png"
        img.save(out)
        rows.append(
            {
                "image_index": i,
                "filename": p.name,
                "image_path": str(p),
                "crop_path": str(out),
                "crop_mode": mode,
                "crop_box_px": box,
                "crop_size_px": list(img.size),
                "notes": note,
            }
        )
        if note:
            run.log(f"crop WARNING image_index={i} {p.name}: {note}")
    # ocr.jsonl carries frame rows; write skeleton now so `ocr` can fill it.
    existing = {r["image_index"]: r for r in run.frames()}
    merged = []
    for r in rows:
        prev = existing.get(r["image_index"], {})
        merged.append({**prev, **r})
    write_jsonl_atomic(run.ocr_path, merged)
    meta = run.meta()
    meta["crop_committed_at"] = _now()
    meta["crop_modes"] = {r["filename"]: r["crop_mode"] for r in rows}
    run.save_meta(meta)
    run.log(f"crop {len(rows)} frames → {run.crops_dir}")
    return merged


def stage_ocr(run: Run) -> list[dict[str, Any]]:
    ensure_tesseract()
    from PIL import Image

    frames = run.frames()
    if not frames:
        raise SystemExit("run `crop` first (ocr.jsonl has no frame rows)")
    for fr in frames:
        img = Image.open(fr["crop_path"])
        text = ocr_image(img, psm=6)
        fr["ocr_text"] = text
        fr["ocr_confidence"] = ocr_confidence(img)
        fr["ocr_engine"] = ENGINE
        fr["thread_markers_raw"] = extract_thread_markers(text)
        if len(text) < 40:
            fr["notes"] = ((fr.get("notes") or "") + "; low_ocr_yield").strip("; ")
    write_jsonl_atomic(run.ocr_path, frames)
    meta = run.meta()
    meta["ocr_committed_at"] = _now()
    run.save_meta(meta)
    run.log(f"ocr {len(frames)} frames")
    return frames


def stage_attribute(run: Run, *, model_mini: str) -> list[dict[str, Any]]:
    frames = run.frames()
    contact = run.contact()
    slug = contact.get("contact_slug") or "contact"
    rows: list[dict[str, Any]] = []
    for fr in frames:
        items = attribute_frame(model_mini, Path(fr["crop_path"]), fr.get("ocr_text") or "", fr["image_index"], slug)
        for it in items:
            rows.append(
                {
                    "record_type": "attributed",
                    "image_index": fr["image_index"],
                    "filename": fr["filename"],
                    "crop_path": fr["crop_path"],
                    **it,
                }
            )
        geo = " ".join(
            f"b{it['local_seq']}:{it['geometry']['color'][0]}{'^' if it['starts_before'] else ''}{'v' if it['ends_after'] else ''}"
            + (f"+{it['reaction_emoji']}" if it.get("reaction_emoji") else "")
            + (f"+pill" if it.get("timestamp_raw") else "")
            + (f"+rr" if it.get("read_receipt") else "")
            for it in items
        )
        run.log(f"attribute image_index={fr['image_index']} {fr['filename']} items={len(items)} [{geo}]")
    write_jsonl_atomic(run.attributed_path, rows)
    meta = run.meta()
    meta["attribute_committed_at"] = _now()
    meta["attributed_item_count"] = len(rows)
    run.save_meta(meta)
    run.log(f"attribute total items={len(rows)}")
    return rows


def _write_transcript(run: Run, messages: list[dict[str, Any]], *, stage: str) -> list[dict[str, Any]]:
    meta = run.meta()
    frames = {int(f["image_index"]): f for f in run.frames()}
    rows = to_transcript_rows(
        messages,
        run_id=meta.get("run_id", run.dir.name),
        frames=frames,
        process_date=meta.get("capture_assumption_date") or datetime.date.today().isoformat(),
        tz=meta.get("processing_timezone") or "America/Los_Angeles",
    )
    write_jsonl_atomic(run.transcript_path, rows)
    meta[f"{stage}_committed_at"] = _now()
    meta["message_count"] = len(rows)
    run.save_meta(meta)
    return rows


def stage_stitch(run: Run, *, model_41: str) -> list[dict[str, Any]]:
    attributed = read_jsonl(run.attributed_path)
    if not attributed:
        raise SystemExit("run `attribute` first (attributed.jsonl empty)")
    contact = run.contact()
    slug = contact.get("contact_slug") or "contact"
    messages = messages_from_attributed(attributed)
    n0 = len(messages)
    messages, pre_log = prestitch(messages)
    for line in pre_log:
        run.log(f"stitch {line}")
    run.log(f"stitch prestitch items={n0} → messages={len(messages)}")
    new_messages, data = run_gpt41_pass(
        model_41, 1, messages=messages, frames=run.frames(), contact_slug=slug, frame_geometry=frame_geometry(attributed, messages)
    )
    data["prestitch_log"] = pre_log
    data["prestitch_message_count"] = len(messages)
    write_json_atomic(run.pass1_path, data)
    rows = _write_transcript(run, new_messages, stage="stitch")
    run.log(f"stitch pass1 ok={data.get('ok')} tool_calls={len(data.get('tool_calls') or [])} issues={len(data.get('issues') or [])} messages={len(rows)}")
    return rows


def stage_review(run: Run, *, model_41: str) -> list[dict[str, Any]]:
    rows = read_jsonl(run.transcript_path)
    if not rows:
        raise SystemExit("run `stitch` first (transcript.jsonl empty)")
    contact = run.contact()
    slug = contact.get("contact_slug") or "contact"
    prior = json.loads(run.pass1_path.read_text(encoding="utf-8")) if run.pass1_path.is_file() else {}
    messages = messages_from_transcript_rows(rows)
    run.log(f"review pass2 start messages={len(messages)}")
    attributed = read_jsonl(run.attributed_path)
    new_messages, data = run_gpt41_pass(
        model_41, 2, messages=messages, frames=run.frames(), contact_slug=slug, prior_pass=prior, frame_geometry=frame_geometry(attributed, messages)
    )
    write_json_atomic(run.pass2_path, data)
    rows = _write_transcript(run, new_messages, stage="review")
    run.log(f"review pass2 ok={data.get('ok')} tool_calls={len(data.get('tool_calls') or [])} issues={len(data.get('issues') or [])} messages={len(rows)}")
    return rows


def stage_scaffold(run: Run) -> str:
    rows = read_jsonl(run.transcript_path)
    if not rows:
        raise SystemExit("transcript.jsonl empty")
    # refresh derived interlocutions in case interlocutions.py changed
    from interlocutions import detect_interlocutions

    for r in rows:
        r["interlocutions"] = detect_interlocutions(r.get("text") or "")
    write_jsonl_atomic(run.transcript_path, rows)
    md = scaffold_report(run.contact(), run.meta(), format_transcript_md(rows), VERSION)
    run.report_path.write_text(md, encoding="utf-8")
    meta = run.meta()
    meta["scaffold_committed_at"] = _now()
    run.save_meta(meta)
    run.log(f"scaffold report.md messages={len(rows)}")
    return md


def stage_report(run: Run, *, model_4o: str) -> None:
    md = run.report_path.read_text(encoding="utf-8")
    if "<!-- gpt4o:" not in md:
        md = stage_scaffold(run)
    rows = read_jsonl(run.transcript_path)
    sections = run_report(run.contact(), run.meta(), rows, model_4o)
    run.report_path.write_text(fill_report(md, sections), encoding="utf-8")
    meta = run.meta()
    meta["report_committed_at"] = _now()
    run.save_meta(meta)
    run.log(f"report {run.report_path}")


# ----------------------------------------------------------------------------- driver


def run_pipeline(
    images_dir: Path,
    out_dir: Path,
    profile_path: Path,
    *,
    slug: str,
    process_date: str,
    tz: str,
    model_mini: str,
    model_41: str,
    model_4o: str,
    stage: str = "all",
    run_dir: Path | None = None,
) -> Path:
    profile = load_profile(profile_path)
    images = list_images(images_dir)
    if not images:
        raise SystemExit(f"no images in {images_dir}")
    models = {"mini": model_mini, "gpt41": model_41, "gpt4o": model_4o}

    if run_dir is None:
        run_id = new_run_id(slug)
        run_dir = out_dir / run_id
    else:
        run_id = run_dir.name
    run = Run(run_dir)

    want = STAGES if stage == "all" else [stage]
    if stage != "all" and stage != "init" and not run.meta_path.is_file():
        stage_init(run, run_id=run_id, images=images, images_dir=images_dir, process_date=process_date, tz=tz, models=models, profile_path=profile_path)

    for s in want:
        if s == "init":
            stage_init(run, run_id=run_id, images=images, images_dir=images_dir, process_date=process_date, tz=tz, models=models, profile_path=profile_path)
        elif s == "contact":
            stage_contact(run, images=images, profile=profile, model_mini=model_mini, process_date=process_date, tz=tz)
        elif s == "crop":
            stage_crop(run, images=images, profile=profile)
        elif s == "ocr":
            stage_ocr(run)
        elif s == "attribute":
            stage_attribute(run, model_mini=model_mini)
        elif s == "stitch":
            stage_stitch(run, model_41=model_41)
        elif s == "review":
            stage_review(run, model_41=model_41)
        elif s == "scaffold":
            stage_scaffold(run)
        elif s == "report":
            stage_report(run, model_4o=model_4o)
        else:
            raise SystemExit(f"unknown stage {s}")
    return run_dir

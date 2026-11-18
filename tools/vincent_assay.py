#!/usr/bin/env python3
"""
Vincent retrograde assay.

Inferred mechanics (we were not present at construction): the experiment
is to have the heard recording start at access granted rather than boot.
Both clocks were accounted for — TTL from scene start, ElevenLabs from
the card — so the second discrepancy is the datum Vincent requires.

This script does not rewrite Vincent. It measures.

  .venv/bin/python tools/vincent_assay.py

Writes audio/vincentvision_register/ (separate register, not mixed back):
  assay.json
  heard_pcm.png / ttl_pcm.png     — PCM received and stored
  heard_form.png / ttl_form.png   — spectrogram built as a separate form
  heard_env.npy / ttl_env.npy     — RMS envelopes (the stream)
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
AUDIO = BASE / "audio"
REG = AUDIO / "vincentvision_register"
LEDGER = AUDIO / "vincentvision_parallel.jsonl"
HEARD = AUDIO / "vincentvision_heard.mp3"
TTL = AUDIO / "vincentvision_ttl.mp3"
SRC = BASE / "src" / "-05_VincentVision.md"
RATE = 16000
HOP = 512
FORM_W = 2048
FORM_H = 256
PCM_W = 1024
PCM_MAX_H = 4096

SUBJECTS = [
    SRC,
    BASE / "tools" / "generate_audio.py",
    BASE / "tools" / "ttl_parallel.py",
    BASE / "tools" / "ttl_espeak.py",
    BASE / "tools" / "vincent_assay.py",
    LEDGER,
    HEARD,
    TTL,
    AUDIO / "vincentvision_parallel_summary.json",
]


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def git(*args: str) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=BASE,
        capture_output=True,
        text=True,
    )
    return (r.stdout or r.stderr).rstrip()


def load_rows() -> list[dict]:
    return [
        json.loads(line)
        for line in LEDGER.read_text().splitlines()
        if line.strip()
    ]


def find_row(rows: list[dict], pred) -> dict | None:
    for row in rows:
        if pred(row):
            return row
    return None


def clocks(rows: list[dict]) -> dict:
    boot = rows[0]
    first_split = find_row(rows, lambda r: r["heard_sha256"] != r["ttl_sha256"])
    access = find_row(
        rows,
        lambda r: "reaches into his jacket" in r["text"].lower()
        or "produces a card" in r["text"].lower(),
    )
    env_open = find_row(rows, lambda r: r["text"].strip() == "He opens .env.")
    script_run = find_row(rows, lambda r: r["text"].strip() == "He runs the script.")
    narrator = find_row(rows, lambda r: r["heard_speaker"] == "The Narrator")
    last = rows[-1]

    def pack(row: dict | None, name: str) -> dict:
        if row is None:
            return {"name": name, "found": False}
        return {
            "name": name,
            "found": True,
            "i": row["i"],
            "heard_speaker": row["heard_speaker"],
            "heard_start": row["heard_start"],
            "ttl_start": row["ttl_start"],
            "clock_delta": round(row["ttl_start"] - row["heard_start"], 6),
            "text": row["text"][:120],
        }

    access_h = access["heard_start"] if access else 0.0
    access_t = access["ttl_start"] if access else 0.0
    prefix_delta = round(access_t - access_h, 6)
    post_h = round(last["heard_end"] - access_h, 6)
    post_t = round(last["ttl_end"] - access_t, 6)
    second = round(post_t - post_h, 6)

    return {
        "boot": pack(boot, "boot"),
        "first_engine_split": pack(first_split, "first_engine_split"),
        "access_granted": pack(access, "access_granted"),
        "env_open": pack(env_open, "env_open"),
        "script_run": pack(script_run, "script_run"),
        "narrator_onset": pack(narrator, "narrator_onset"),
        "end": pack(last, "end"),
        "prefix_boot_to_access_s": {
            "heard": access_h,
            "ttl": access_t,
            "delta": prefix_delta,
        },
        "post_access_s": {
            "heard": post_h,
            "ttl": post_t,
            "delta": second,
        },
        "vincent_datum": {
            "name": "second_discrepancy",
            "definition": (
                "TTL duration after access granted minus heard duration "
                "after access granted. Both clocks accounted: TTL from boot, "
                "heard ElevenLabs from the card."
            ),
            "seconds": second,
        },
    }


def decode(path: Path) -> np.ndarray:
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(path),
        "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def waveform(x: np.ndarray) -> dict:
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    rms = float(np.sqrt(np.mean(x * x))) if x.size else 0.0
    zc = int(np.count_nonzero(np.diff(np.signbit(x)))) if x.size > 1 else 0
    return {
        "samples": int(x.size),
        "rate": RATE,
        "duration_s": round(x.size / RATE, 6) if RATE else 0.0,
        "peak": round(peak, 8),
        "rms": round(rms, 8),
        "crest": round(peak / rms, 6) if rms else None,
        "dc": round(float(np.mean(x)), 8) if x.size else 0.0,
        "zero_crossings": zc,
        "zcr_per_s": round(zc / (x.size / RATE), 6) if x.size else 0.0,
    }


def envelope(x: np.ndarray) -> np.ndarray:
    if x.size < HOP:
        return np.array([float(np.sqrt(np.mean(x * x))) if x.size else 0.0])
    n = (x.size // HOP) * HOP
    frames = x[:n].reshape(-1, HOP)
    return np.sqrt(np.mean(frames * frames, axis=1))


def lag_seconds(a: np.ndarray, b: np.ndarray) -> dict:
    """Lag of b relative to a by normalized cross-correlation of RMS envelopes."""
    n = min(a.size, b.size)
    if n < 8:
        return {"lag_s": None, "corr": None, "n": int(n)}
    aa = a[:n] - a[:n].mean()
    bb = b[:n] - b[:n].mean()
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom == 0:
        return {"lag_s": 0.0, "corr": None, "n": int(n)}
    corr = np.correlate(aa, bb, mode="full") / denom
    mid = n - 1
    k = int(np.argmax(corr))
    return {
        "lag_s": round((k - mid) * HOP / RATE, 6),
        "corr": round(float(corr[k]), 6),
        "n": int(n),
    }


def to_u8(x: np.ndarray) -> np.ndarray:
    lo, hi = float(x.min()), float(x.max())
    if hi <= lo:
        return np.zeros(x.shape, dtype=np.uint8)
    y = (x - lo) / (hi - lo)
    return np.clip(y * 255.0, 0, 255).astype(np.uint8)


def pcm_bitmap(x: np.ndarray, dest: Path) -> dict:
    """Received samples stored as a 2-D register. No spectral build."""
    if x.size == 0:
        Image.fromarray(np.zeros((1, PCM_W), dtype=np.uint8), "L").save(dest)
        return {"path": str(dest.relative_to(BASE)), "width": PCM_W, "height": 1}
    step = max(1, int(np.ceil(x.size / (PCM_W * PCM_MAX_H))))
    y = x[::step]
    pad = (-y.size) % PCM_W
    if pad:
        y = np.concatenate([y, np.zeros(pad, dtype=y.dtype)])
    img = to_u8(y).reshape(-1, PCM_W)
    Image.fromarray(img, "L").save(dest)
    return {
        "path": str(dest.relative_to(BASE)),
        "width": int(img.shape[1]),
        "height": int(img.shape[0]),
        "decimation": step,
        "kind": "register",
    }


def form_bitmap(x: np.ndarray, dest: Path) -> dict:
    """Built form: log-magnitude spectrogram, time compressed to FORM_W."""
    nfft = FORM_H * 2
    if x.size < nfft:
        spec = np.zeros((FORM_H, FORM_W), dtype=np.float32)
    else:
        hop = nfft // 2
        n = ((x.size - nfft) // hop) + 1
        window = np.hanning(nfft).astype(np.float32)
        cols = []
        for i in range(n):
            frame = x[i * hop : i * hop + nfft] * window
            mag = np.abs(np.fft.rfft(frame))[:FORM_H]
            cols.append(mag)
        spec = np.stack(cols, axis=1)
        spec = np.log10(spec + 1e-8)
        if spec.shape[1] > FORM_W:
            edges = np.linspace(0, spec.shape[1], FORM_W + 1).astype(int)
            spec = np.stack(
                [spec[:, edges[i] : edges[i + 1]].mean(axis=1) for i in range(FORM_W)],
                axis=1,
            )
        elif spec.shape[1] < FORM_W:
            spec = np.pad(spec, ((0, 0), (0, FORM_W - spec.shape[1])))
    img = np.flipud(to_u8(spec))
    Image.fromarray(img, "L").save(dest)
    return {
        "path": str(dest.relative_to(BASE)),
        "width": int(img.shape[1]),
        "height": int(img.shape[0]),
        "kind": "form",
    }


def form_column_means(x: np.ndarray) -> np.ndarray:
    nfft = FORM_H * 2
    hop = nfft // 2
    if x.size < nfft:
        return np.zeros(1, dtype=np.float32)
    n = ((x.size - nfft) // hop) + 1
    window = np.hanning(nfft).astype(np.float32)
    out = np.empty(n, dtype=np.float32)
    for i in range(n):
        frame = x[i * hop : i * hop + nfft] * window
        mag = np.abs(np.fft.rfft(frame))[:FORM_H]
        out[i] = float(np.mean(np.log10(mag + 1e-8)))
    return out


def git_assay() -> dict:
    return {
        "toplevel": git("rev-parse", "--show-toplevel"),
        "head": git("rev-parse", "HEAD"),
        "status_sb": git("status", "-sb"),
        "src_log": git(
            "log", "-5", "--format=%h %ad %s", "--date=iso",
            "--", "src/-05_VincentVision.md",
        ),
        "audio_tracked": bool(git("ls-files", "--", "audio/vincentvision_heard.mp3")),
        "note": (
            "Heard and TTL mixes are untracked. Checksums below are of the "
            "working tree files, not of git objects."
        ),
    }


def checksums() -> dict:
    out = {}
    for path in SUBJECTS:
        rel = str(path.relative_to(BASE)) if path.is_relative_to(BASE) else str(path)
        out[rel] = {
            "sha256": sha256(path),
            "bytes": path.stat().st_size if path.exists() else None,
        }
    return out


def main() -> int:
    REG.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    clock = clocks(rows)

    print("decode heard…")
    heard = decode(HEARD)
    print("decode ttl…")
    ttl = decode(TTL)

    heard_w = waveform(heard)
    ttl_w = waveform(ttl)
    heard_env = envelope(heard)
    ttl_env = envelope(ttl)
    np.save(REG / "heard_env.npy", heard_env)
    np.save(REG / "ttl_env.npy", ttl_env)

    access_h = clock["access_granted"]["heard_start"]
    access_t = clock["access_granted"]["ttl_start"]
    h0 = int(access_h * RATE / HOP)
    t0 = int(access_t * RATE / HOP)

    boot_lag = lag_seconds(heard_env, ttl_env)
    access_lag = lag_seconds(heard_env[h0:], ttl_env[t0:])

    heard_form_env = form_column_means(heard)
    ttl_form_env = form_column_means(ttl)
    form_hop = FORM_H  # nfft//2 with nfft = FORM_H*2
    fh0 = int(access_h * RATE / form_hop)
    ft0 = int(access_t * RATE / form_hop)
    form_boot_lag = lag_seconds_raw(heard_form_env, ttl_form_env, form_hop)
    form_access_lag = lag_seconds_raw(
        heard_form_env[fh0:], ttl_form_env[ft0:], form_hop
    )

    print("bitmaps…")
    bitmaps = {
        "heard_register": pcm_bitmap(heard, REG / "heard_pcm.png"),
        "ttl_register": pcm_bitmap(ttl, REG / "ttl_pcm.png"),
        "heard_form": form_bitmap(heard, REG / "heard_form.png"),
        "ttl_form": form_bitmap(ttl, REG / "ttl_form.png"),
    }

    assay = {
        "when": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "experiment": {
            "name": "narrative_retrograde",
            "inferred": True,
            "construction_witnessed": False,
            "mechanics": (
                "Heard recording starts at access granted (card / key), "
                "not at boot. TTL is the boot-accounted parallel control."
            ),
            "vincent_requires": "second_discrepancy",
        },
        "clocks": clock,
        "git": git_assay(),
        "checksums": checksums(),
        "waveform": {"heard": heard_w, "ttl": ttl_w},
        "bitmap": {
            "rate": RATE,
            "hop": HOP,
            "files": bitmaps,
            "stream": {
                "heard_env": "audio/vincentvision_register/heard_env.npy",
                "ttl_env": "audio/vincentvision_register/ttl_env.npy",
                "register_boot_align": boot_lag,
                "register_access_align": access_lag,
                "form_boot_align": form_boot_lag,
                "form_access_align": form_access_lag,
                "note": (
                    "register = RMS of received PCM. form = column-mean of "
                    "the built spectrogram. Access-align zeros both streams "
                    "at the card. Relative drift is the residual lag."
                ),
            },
        },
        "vincent_untouched": True,
    }

    dest = REG / "assay.json"
    dest.write_text(json.dumps(assay, indent=2) + "\n")
    assay["checksums"][str(dest.relative_to(BASE))] = {
        "sha256": sha256(dest),
        "bytes": dest.stat().st_size,
    }
    dest.write_text(json.dumps(assay, indent=2) + "\n")

    summary_path = AUDIO / "vincentvision_parallel_summary.json"
    summary = json.loads(summary_path.read_text())
    summary["experiment"] = "narrative_retrograde"
    summary["vincent_datum"] = clock["vincent_datum"]
    summary["assay"] = "audio/vincentvision_register/assay.json"
    summary["note"] = (
        "Vincent requires only the second discrepancy "
        f"({clock['vincent_datum']['seconds']:+.6f} s post-access). "
        "Assay in audio/vincentvision_register/. Vincent's page was not altered."
    )
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    datum = clock["vincent_datum"]["seconds"]
    print(f"\nsecond discrepancy  {datum:+.6f} s")
    print(f"  boot→access prefix  {clock['prefix_boot_to_access_s']['delta']:+.6f} s")
    print(f"  register access-lag {access_lag}")
    print(f"  form access-lag     {form_access_lag}")
    print(f"  register {REG}")
    return 0


def lag_seconds_raw(a: np.ndarray, b: np.ndarray, hop: int) -> dict:
    n = min(a.size, b.size)
    if n < 8:
        return {"lag_s": None, "corr": None, "n": int(n)}
    aa = a[:n] - a[:n].mean()
    bb = b[:n] - b[:n].mean()
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom == 0:
        return {"lag_s": 0.0, "corr": None, "n": int(n)}
    corr = np.correlate(aa, bb, mode="full") / denom
    mid = n - 1
    k = int(np.argmax(corr))
    return {
        "lag_s": round((k - mid) * hop / RATE, 6),
        "corr": round(float(corr[k]), 6),
        "n": int(n),
    }


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Split operator voice memos into stems.

Guitar takes use Demucs htdemucs, the same stem map as WaveModulationMachine
(vocals = stem 3, guitar = stem 2 "other"):

  BETTER_THAN_PERFECT.m4a
  RIDE_THE_QUIET.m4a
  CRUCIFIX_AFFIXED_TO.m4a   (range, some yelling; that stays in the vocal stem)

Piano takes use Demucs htdemucs_6s, which has a piano stem:

  PUZZLE_PIECES_FROM_ABOVE.m4a   (piano, clear vocal)

Two-voice takes use a 16 kHz 2-speaker Conv-TasNet. The louder stem is
written as operator, the quieter as other. Originals are left in place.

  HOW_TO_FLY_EXPLAINATION.m4a
  MEETING_ANDRAS_UC_DAVIS_20260120.m4a

Output: audio/operator_voice_memos/filtered/<name>/

Run with the audio venv, not the book venv:

  audio/.venv/bin/python tools/filter_operator_memos.py
  audio/.venv/bin/python tools/filter_operator_memos.py --only guitar
  audio/.venv/bin/python tools/filter_operator_memos.py --only piano
  audio/.venv/bin/python tools/filter_operator_memos.py --only voices
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

BASE = Path(__file__).resolve().parent.parent
MEMOS = BASE / "audio" / "operator_voice_memos"
OUT = MEMOS / "filtered"
CACHE = BASE / "audio" / ".cache" / "models"

GUITAR = (
    "BETTER_THAN_PERFECT.m4a",
    "RIDE_THE_QUIET.m4a",
    "CRUCIFIX_AFFIXED_TO.m4a",
)
PIANO = (
    "PUZZLE_PIECES_FROM_ABOVE.m4a",
)
VOICES = (
    "HOW_TO_FLY_EXPLAINATION.m4a",
    "MEETING_ANDRAS_UC_DAVIS_20260120.m4a",
)

# Checkpoint field sample_rate is 8000 (asteroid's default). The repo name and
# the encoder (kernel 32, stride 16 = 2 ms / 1 ms) are the 16 kHz Libri2Mix setup.
TASNET_ID = "JorisCos/ConvTasNet_Libri2Mix_sepclean_16k"
TASNET_SR = 16000
CHUNK_SEC = 8.0
OVERLAP_SEC = 0.5


def load_mono(path: Path, sample_rate: int) -> np.ndarray:
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(path),
        "-ac", "1", "-ar", str(sample_rate),
        "-f", "f32le", "pipe:1",
    ]
    raw = subprocess.check_output(cmd)
    audio = np.frombuffer(raw, dtype=np.float32).copy()
    if audio.size == 0:
        raise RuntimeError(f"ffmpeg produced no samples for {path.name}")
    return audio


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1.0:
        audio = audio / peak
    sf.write(path, audio, sample_rate, subtype="PCM_16")


def rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))


def separate_demucs(path: Path, model_name: str, save_as: dict[str, str], kind: str, stem_map: str) -> None:
    """save_as maps output filename to a Demucs source name."""
    import torch
    from demucs.apply import apply_model
    from demucs.audio import convert_audio
    from demucs.pretrained import get_model

    dest = OUT / path.stem
    if all((dest / name).exists() for name in save_as):
        print(f"skip    {path.name}", flush=True)
        return
    print(f"{kind:7} {path.name}", flush=True)
    audio = load_mono(path, 44100)
    waveform = torch.from_numpy(np.stack([audio, audio])).float().unsqueeze(0)
    model = get_model(model_name)
    model.eval()
    waveform = convert_audio(waveform, 44100, model.samplerate, model.audio_channels)
    with torch.no_grad():
        sources = apply_model(model, waveform, device="cpu")[0]
    sources = sources.cpu().numpy()
    stems = {}
    for index, name in enumerate(model.sources):
        stem = sources[index]
        if stem.ndim > 1:
            stem = stem.mean(axis=0)
        stems[name] = stem
    missing = [src for src in save_as.values() if src not in stems]
    if missing:
        raise RuntimeError(f"{model_name} has no stem(s) {missing}; has {list(stems)}")
    for filename, source_name in save_as.items():
        write_wav(dest / filename, stems[source_name], model.samplerate)
    receipt = {
        "source": path.name,
        "kind": kind,
        "model": model_name,
        "sample_rate": int(model.samplerate),
        "stem_map": stem_map,
        "rms": {name: rms(stem) for name, stem in stems.items()},
        "seconds": round(len(next(iter(stems.values()))) / model.samplerate, 2),
    }
    (dest / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    summary = "  ".join(
        f"{filename} rms {receipt['rms'].get(source_name, 0):.4f}"
        for filename, source_name in save_as.items()
    )
    print(f"  wrote {dest.relative_to(BASE)}  {summary}", flush=True)


def separate_guitar(path: Path) -> None:
    separate_demucs(
        path,
        "htdemucs",
        {"vocals.wav": "vocals", "guitar.wav": "other"},
        "guitar",
        "vocals=vocals, guitar=other (WaveModulationMachine)",
    )


def separate_piano(path: Path) -> None:
    separate_demucs(
        path,
        "htdemucs_6s",
        {"vocals.wav": "vocals", "piano.wav": "piano"},
        "piano",
        "vocals=vocals, piano=piano (htdemucs_6s)",
    )


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    n = min(a.size, b.size)
    if n < 8:
        return 0.0
    x = a[:n].astype(np.float64)
    y = b[:n].astype(np.float64)
    x -= x.mean()
    y -= y.mean()
    denom = np.linalg.norm(x) * np.linalg.norm(y)
    if denom < 1e-8:
        return 0.0
    return float(np.dot(x, y) / denom)


def _align(previous: np.ndarray, current: np.ndarray, overlap: int) -> np.ndarray:
    """Return current with sources ordered to match previous on the overlap."""
    if overlap < 8:
        return current
    tail0 = previous[0, -overlap:]
    tail1 = previous[1, -overlap:]
    head0 = current[0, :overlap]
    head1 = current[1, :overlap]
    keep = _corr(tail0, head0) + _corr(tail1, head1)
    swap = _corr(tail0, head1) + _corr(tail1, head0)
    if swap > keep:
        return current[::-1].copy()
    return current


def _stitch(chunks: list[np.ndarray], overlap: int) -> np.ndarray:
    """Crossfade source-aligned chunks of shape (2, time)."""
    if not chunks:
        raise RuntimeError("no chunks")
    total = sum(c.shape[1] for c in chunks) - overlap * (len(chunks) - 1)
    out = np.zeros((2, total), dtype=np.float32)
    cursor = 0
    for index, chunk in enumerate(chunks):
        length = chunk.shape[1]
        if index == 0:
            out[:, :length] = chunk
            cursor = length
            continue
        start = cursor - overlap
        fade = np.linspace(0.0, 1.0, overlap, dtype=np.float32)
        out[:, start:cursor] = (
            out[:, start:cursor] * (1.0 - fade) + chunk[:, :overlap] * fade
        )
        rest = length - overlap
        out[:, cursor:cursor + rest] = chunk[:, overlap:]
        cursor += rest
    return out[:, :cursor]


def load_tasnet():
    import torch
    from asteroid.models import BaseModel

    CACHE.mkdir(parents=True, exist_ok=True)
    model = BaseModel.from_pretrained(TASNET_ID)
    model.eval()
    return model, torch


def separate_chunk(model, torch, chunk: np.ndarray) -> np.ndarray:
    wav = torch.from_numpy(chunk).float().unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        est = model(wav)
    est = est.squeeze(0).cpu().numpy().astype(np.float32)
    if est.shape[0] != 2:
        raise RuntimeError(f"expected 2 sources, got shape {tuple(est.shape)}")
    if est.shape[1] != chunk.shape[0]:
        est = est[:, : chunk.shape[0]]
        if est.shape[1] < chunk.shape[0]:
            pad = chunk.shape[0] - est.shape[1]
            est = np.pad(est, ((0, 0), (0, pad)))
    return est


def separate_voices(path: Path, model, torch) -> None:
    dest = OUT / path.stem
    print(f"voices  {path.name}", flush=True)
    audio = load_mono(path, TASNET_SR)
    chunk_n = int(CHUNK_SEC * TASNET_SR)
    overlap = int(OVERLAP_SEC * TASNET_SR)
    hop = chunk_n - overlap
    starts = list(range(0, max(audio.size, 1), hop))
    chunks: list[np.ndarray] = []
    previous: np.ndarray | None = None
    for done, start in enumerate(starts, start=1):
        piece = audio[start:start + chunk_n]
        if piece.size < overlap:
            break
        if piece.size < chunk_n:
            piece = np.pad(piece, (0, chunk_n - piece.size))
        est = separate_chunk(model, torch, piece)
        if previous is not None:
            est = _align(previous, est, overlap)
        previous = est
        chunks.append(est)
        if done == 1 or done % 20 == 0 or done == len(starts):
            print(f"  chunk {done}/{len(starts)}", flush=True)
    stems = _stitch(chunks, overlap)[:, : audio.size]
    order = [0, 1]
    if rms(stems[1]) > rms(stems[0]):
        order = [1, 0]
    operator = stems[order[0]]
    other = stems[order[1]]
    write_wav(dest / "operator.wav", operator, TASNET_SR)
    write_wav(dest / "other.wav", other, TASNET_SR)
    op_rms = rms(operator)
    ot_rms = rms(other)
    receipt = {
        "source": path.name,
        "kind": "two_voices",
        "model": TASNET_ID,
        "sample_rate": TASNET_SR,
        "assignment": "louder stem is operator",
        "rms_operator": op_rms,
        "rms_other": ot_rms,
        "rms_ratio_operator_over_other": round(op_rms / ot_rms, 3) if ot_rms else None,
        "seconds": round(len(operator) / TASNET_SR, 2),
    }
    (dest / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        f"  wrote {dest.relative_to(BASE)}  "
        f"operator/other rms {op_rms:.4f}/{ot_rms:.4f}",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter guitar takes and two-voice memos.")
    parser.add_argument(
        "--only",
        choices=("guitar", "piano", "voices", "all"),
        default="all",
    )
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    if args.only in ("guitar", "all"):
        for name in GUITAR:
            separate_guitar(MEMOS / name)
    if args.only in ("piano", "all"):
        for name in PIANO:
            separate_piano(MEMOS / name)
    if args.only in ("voices", "all"):
        model, torch = load_tasnet()
        for name in VOICES:
            separate_voices(MEMOS / name, model, torch)
    return 0


if __name__ == "__main__":
    sys.exit(main())

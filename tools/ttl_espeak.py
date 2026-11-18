#!/usr/bin/env python3
"""
TTL narrator: libespeak-ng via ctypes.

Limited on purpose. Does not have to sound good. Does not have to
express recognizable words. Parallel track for the retrograde experiment.
"""

from __future__ import annotations

import ctypes
import struct
import subprocess
import wave
from pathlib import Path

LIB = ctypes.CDLL("libespeak-ng.so.1")
DATA = "/usr/lib/x86_64-linux-gnu/espeak-ng-data"

AUDIO_OUTPUT_RETRIEVAL = 1
ESPEAK_CHARS_UTF8 = 1

LIB.espeak_Initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
LIB.espeak_Initialize.restype = ctypes.c_int
LIB.espeak_SetVoiceByName.argtypes = [ctypes.c_char_p]
LIB.espeak_SetParameter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
LIB.espeak_Synth.argtypes = [
    ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint, ctypes.c_int,
    ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint), ctypes.c_void_p,
]
LIB.espeak_Synchronize.restype = ctypes.c_int
LIB.espeak_Terminate.restype = ctypes.c_int

# espeak_PARAMETER: RATE=1, PITCH=3, RANGE=4, VOLUME=2
RATE, VOLUME, PITCH, RANGE = 1, 2, 3, 4

CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_short),
    ctypes.c_int,
    ctypes.c_void_p,
)
LIB.espeak_SetSynthCallback.argtypes = [CALLBACK]

_chunks: list[bytes] = []
_rate_hz = 22050


def _cb(wav, n, _events):
    if n > 0 and wav:
        _chunks.append(ctypes.string_at(wav, n * 2))
    return 0


_cb_ref = CALLBACK(_cb)


def synthesize_wav(text: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    _chunks.clear()
    rate = LIB.espeak_Initialize(AUDIO_OUTPUT_RETRIEVAL, 0, DATA.encode(), 0)
    if rate > 0:
        global _rate_hz
        _rate_hz = rate
    LIB.espeak_SetSynthCallback(_cb_ref)
    LIB.espeak_SetVoiceByName(b"en-us")
    LIB.espeak_SetParameter(RATE, 135, 0)
    LIB.espeak_SetParameter(PITCH, 28, 0)
    LIB.espeak_SetParameter(RANGE, 10, 0)
    LIB.espeak_SetParameter(VOLUME, 80, 0)
    raw = text.encode("utf-8") + b"\x00"
    LIB.espeak_Synth(raw, len(raw), 0, 0, 0, ESPEAK_CHARS_UTF8, None, None)
    LIB.espeak_Synchronize()
    LIB.espeak_Terminate()
    dest.write_bytes(_wav_bytes(b"".join(_chunks), _rate_hz))
    return dest


def _wav_bytes(pcm: bytes, rate: int) -> bytes:
    buf = bytearray()
    # wave module wants a file; write header by hand if empty
    import io
    bio = io.BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm or struct.pack("<h", 0))
    return bio.getvalue()


def to_mp3(text: str, dest: Path) -> Path:
    wav = dest.with_suffix(".wav")
    synthesize_wav(text, wav)
    cmd = [
        "ffmpeg", "-y", "-i", str(wav),
        "-codec:a", "libmp3lame", "-q:a", "5",
        str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True)
    wav.unlink(missing_ok=True)
    if r.returncode != 0 or not dest.exists():
        raise RuntimeError(r.stderr.decode()[:400])
    return dest

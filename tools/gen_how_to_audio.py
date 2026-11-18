#!/usr/bin/env python3
"""
gen_how_to_audio.py — Generate ElevenLabs narration for all how_tos.
Voice: Matilda (XrExE9yKIg1WjnnlVkGX) by default.
Outputs: how_tos/{slug}/audio.mp3

Usage:
    .venv/bin/python tools/gen_how_to_audio.py [--slug how-to-fly] [--force]

Requires ELEVENLABS_API_KEY in environment or .env file.
"""
import os, sys, json, argparse, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

BASE  = pathlib.Path(__file__).parent.parent
HT    = BASE / "how_tos"
DATA  = HT / "data.json"

MATILDA_VOICE   = "XrExE9yKIg1WjnnlVkGX"
XI_API_BASE     = "https://api.elevenlabs.io/v1"
CHUNK_CHARS     = 4800  # ElevenLabs free tier ~5000 char limit per call

def load_env():
    env_path = BASE / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))

def get_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print("ERROR: ELEVENLABS_API_KEY not set. Add it to .env or export it.")
        sys.exit(1)
    return key

def narrate_text(text: str, voice_id: str, api_key: str) -> bytes:
    """Call ElevenLabs TTS API, return mp3 bytes."""
    import urllib.request, urllib.error
    url = f"{XI_API_BASE}/text-to-speech/{voice_id}"
    payload = json.dumps({
        "text": text[:CHUNK_CHARS],
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.42, "similarity_boost": 0.75}
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"ElevenLabs error {e.code}: {body}")

def extract_plain_text(md_path: pathlib.Path) -> str:
    """Strip markdown syntax for cleaner narration."""
    import re
    text = md_path.read_text()
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'^\|.+\|$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[-*]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def gen_audio_for(slug: str, api_key: str, force: bool = False):
    folder = HT / slug
    source_md = folder / "source.md"
    out_mp3   = folder / "audio.mp3"

    if out_mp3.exists() and not force:
        print(f"  {slug}: audio.mp3 exists (skip, use --force to regenerate)")
        return

    if not source_md.exists():
        print(f"  {slug}: no source.md — skip")
        return

    text = extract_plain_text(source_md)
    if not text or "Source not yet written" in text:
        print(f"  {slug}: no real content — skip")
        return

    print(f"  {slug}: generating audio ({len(text)} chars)…", end="", flush=True)
    try:
        audio = narrate_text(text, MATILDA_VOICE, api_key)
        out_mp3.write_bytes(audio)
        print(f" ✓ ({len(audio)//1024}k)")
    except Exception as e:
        print(f" ✗ {e}")
    time.sleep(0.5)  # rate limit courtesy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Only generate for this slug")
    parser.add_argument("--force", action="store_true", help="Regenerate existing audio")
    args = parser.parse_args()

    load_env()
    api_key = get_api_key()

    data = json.loads(DATA.read_text())
    how_tos = data["how_tos"]

    if args.slug:
        how_tos = [h for h in how_tos if h["id"] == args.slug]
        if not how_tos:
            print(f"No how_to found with slug: {args.slug}")
            sys.exit(1)

    print(f"Generating audio for {len(how_tos)} how_to(s) — Matilda voice")
    for ht in how_tos:
        gen_audio_for(ht["id"], api_key, force=args.force)

if __name__ == "__main__":
    main()

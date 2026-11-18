#!/usr/bin/env python3
"""
save_voice_preview.py — save a generated ElevenLabs voice preview as a named voice.

Usage:
    .venv/bin/python tools/save_voice_preview.py --id <generated_voice_id> --name "Snake"
    .venv/bin/python tools/save_voice_preview.py --id boGH78QQh8VzxUtvPuf6 --name "Goat TTL"

After saving, the script prints the new voice_id and offers to write it to .env.
"""

import argparse
import os
import sys
import requests

def main():
    parser = argparse.ArgumentParser(description="Save an ElevenLabs voice preview as a named voice.")
    parser.add_argument("--id", required=True, help="generated_voice_id from create-previews response")
    parser.add_argument("--name", required=True, help="Name to give the saved voice")
    parser.add_argument("--description", default="", help="Optional description")
    parser.add_argument("--env-key", default="", help="If set, write voice_id to .env under this key (e.g. VOICE_SNAKE)")
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        # Try loading from .env
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            for line in open(env_path):
                line = line.strip()
                if line.startswith("ELEVENLABS_API_KEY="):
                    api_key = line.split("=", 1)[1]
                    break
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found in environment or .env")
        sys.exit(1)

    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    print(f"Saving preview '{args.id}' as voice '{args.name}'...")
    r = requests.post(
        "https://api.elevenlabs.io/v1/text-to-voice/create-voice-from-preview",
        headers=headers,
        json={
            "generated_voice_id": args.id,
            "voice_name": args.name,
            "voice_description": args.description or f"Voice saved from preview. Generated voice id: {args.id}",
            "labels": {},
        },
    )

    if r.status_code not in (200, 201):
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)

    data = r.json()
    voice_id = data.get("voice_id", "")
    print(f"\n✓ Voice saved.")
    print(f"  name:     {args.name}")
    print(f"  voice_id: {voice_id}")

    if args.env_key:
        _write_env(args.env_key, voice_id)
    else:
        print(f"\nTo use this voice, add to .env:")
        print(f"  VOICE_{args.name.upper().replace(' ', '_')}={voice_id}")
        print(f"\nOr re-run with --env-key VOICE_{args.name.upper().replace(' ', '_')} to write automatically.")


def _write_env(key, value):
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(env_path):
        print(f"  .env not found at {env_path}; cannot write.")
        return

    lines = open(env_path).readlines()
    updated = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)
    print(f"  ✓ Wrote {key}={value} to .env")


if __name__ == "__main__":
    main()

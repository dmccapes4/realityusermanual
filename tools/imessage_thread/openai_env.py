"""Load OPENAI_API_KEY from REALITY_USER_MANUAL/.env."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = REPO_ROOT / ".env"


def load_openai_key() -> str:
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip()
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        print("OPENAI_API_KEY required", file=sys.stderr)
        raise SystemExit(1)
    return key


def client():
    from openai import OpenAI

    return OpenAI(api_key=load_openai_key(), max_retries=2)

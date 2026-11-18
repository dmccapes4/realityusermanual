#!/usr/bin/env bash
# Verify Tesseract is available for imessage_thread OCR (run on host).
set -euo pipefail
if ! command -v tesseract >/dev/null 2>&1; then
  echo "tesseract not found. Install on the host, e.g.:"
  echo "  sudo apt-get install -y tesseract-ocr"
  exit 1
fi
tesseract --version | head -1

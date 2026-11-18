#!/bin/bash
# tools/decode_toc.sh
# PNG → PPM → awk finds the header boundary → read length prefix → extract payload → gunzip
# Usage: ./decode_toc.sh [output.json]
# Default output: /tmp/rum_matrix_recovered.json

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

PNG_IN="$PROJECT_DIR/assets/mischievouslittlechicken.png"
PPM_TMP="/tmp/rum_chicken_decode.ppm"
OUT_JSON="${1:-/tmp/rum_matrix_recovered.json}"

echo "[decode] PNG → PPM"
ffmpeg -y -i "$PNG_IN" -pix_fmt rgb24 "$PPM_TMP" 2>/dev/null

# awk: find the exact byte offset where pixel data begins
HEADER_BYTES=$(awk '
NR == 1 { hdr = length($0) + 1 }
NR == 2 { hdr += length($0) + 1 }
NR == 3 { hdr += length($0) + 1; print hdr; exit }
' "$PPM_TMP")

echo "[decode] header: $HEADER_BYTES bytes, pixel data starts at byte $HEADER_BYTES"

# Read 4-byte big-endian payload length using od
PAYLOAD_SIZE=$(dd if="$PPM_TMP" bs=1 skip="$HEADER_BYTES" count=4 2>/dev/null \
    | od -A n -t u1 \
    | awk '{ print ($1 * 16777216) + ($2 * 65536) + ($3 * 256) + $4 }')

echo "[decode] payload size: $PAYLOAD_SIZE bytes"

# Extract payload and gunzip
dd if="$PPM_TMP" bs=1 skip=$(( HEADER_BYTES + 4 )) count="$PAYLOAD_SIZE" 2>/dev/null \
    | gunzip > "$OUT_JSON"

echo "[decode] recovered: $(wc -c < "$OUT_JSON") bytes → $OUT_JSON"

# Verify it's valid JSON
python3 -c "import json,sys; json.load(open('$OUT_JSON')); print('[decode] JSON valid ✓')"

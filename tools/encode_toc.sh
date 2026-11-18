#!/bin/bash
# tools/encode_toc.sh
# PNG → PPM → awk reads the bitmap, payload written to pixel space → PPM → PNG
# The image is the medium. The pixel bytes are the data.
#
# Encoding layout (pixel stream, 18696 bytes for 76x82 RGB):
#   [0:4]             4-byte big-endian payload length
#   [4:4+N]           gzipped matrix.json (N bytes)
#   [4+N:18696]       zero padding
#
# Roundtrip is lossless: PNG→PPM→PNG→PPM pixel bytes are identical.
# Verified 2026-10-29.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

PNG_IN="$PROJECT_DIR/assets/mischievouslittlechicken.png"
MATRIX="$PROJECT_DIR/matrix.json"
PPM_RAW="/tmp/rum_chicken_raw.ppm"
PPM_ENC="/tmp/rum_chicken_encoded.ppm"
PNG_OUT="$PROJECT_DIR/assets/mischievouslittlechicken.png"

echo "[encode] PNG → PPM"
ffmpeg -y -i "$PNG_IN" -pix_fmt rgb24 "$PPM_RAW" 2>/dev/null
echo "[encode] $(wc -c < "$PPM_RAW") bytes raw"

echo "[encode] gzip matrix.json"
gzip -9 -c "$MATRIX" > /tmp/rum_payload.gz
PAYLOAD_SIZE=$(wc -c < /tmp/rum_payload.gz)
echo "[encode] payload: $PAYLOAD_SIZE bytes"

# awk: parse the PPM header, return pixel space size and header byte count
read PIXEL_BYTES HEADER_BYTES < <(awk '
NR == 1 { hdr = length($0) + 1 }
NR == 2 { hdr += length($0) + 1; w = $1+0; h = $2+0 }
NR == 3 { hdr += length($0) + 1; print w*h*3, hdr; exit }
' "$PPM_RAW")

echo "[encode] pixel space: $PIXEL_BYTES bytes  header: $HEADER_BYTES bytes"

NEED=$(( PAYLOAD_SIZE + 4 ))
if [ "$NEED" -gt "$PIXEL_BYTES" ]; then
    echo "[encode] ERROR: payload+prefix ($NEED) exceeds pixel space ($PIXEL_BYTES)" >&2
    exit 1
fi

PAD=$(( PIXEL_BYTES - 4 - PAYLOAD_SIZE ))

# Build encoded PPM: header unchanged + 4-byte length + payload + zeros
{
    # Header: exact bytes from the original
    dd if="$PPM_RAW" bs=1 count="$HEADER_BYTES" 2>/dev/null

    # 4-byte big-endian payload length
    printf "$(printf '\\x%02x\\x%02x\\x%02x\\x%02x' \
        $(( (PAYLOAD_SIZE >> 24) & 0xFF )) \
        $(( (PAYLOAD_SIZE >> 16) & 0xFF )) \
        $(( (PAYLOAD_SIZE >>  8) & 0xFF )) \
        $(( PAYLOAD_SIZE         & 0xFF )))"

    # Payload
    cat /tmp/rum_payload.gz

    # Zero padding
    dd if=/dev/zero bs=1 count="$PAD" 2>/dev/null
} > "$PPM_ENC"

echo "[encode] encoded PPM: $(wc -c < "$PPM_ENC") bytes"

echo "[encode] PPM → PNG"
ffmpeg -y -i "$PPM_ENC" -pix_fmt rgb24 "$PNG_OUT" 2>/dev/null
echo "[encode] PNG: $(wc -c < "$PNG_OUT") bytes"
echo "[encode] done — matrix.json is the chicken"

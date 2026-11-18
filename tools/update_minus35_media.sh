#!/usr/bin/env bash
# Copy updated -35 media into web/listen/media/ (needs write access to the dir)
# Run this from REALITY_USER_MANUAL root

set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"

cp -v "$BASE/video/minus35/-35_the_ridiculous_journey.mp4" \
      "$BASE/web/listen/media/-35_the_ridiculous_journey.mp4"

cp -v "$BASE/audio/minus35/minus35.mp3" \
      "$BASE/web/listen/media/-35.mp3"

echo "Done."

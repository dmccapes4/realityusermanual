#!/usr/bin/env bash
# download_morphgnt.sh — fetch MorphGNT SBL GNT files
#
# MorphGNT: https://github.com/morphgnt/sblgnt  (CC BY-SA 4.0)
# Format: 7 space-separated fields per word:
#   BCVword  part-of-speech  parse-code  text  word  normalized  lemma
#
# BCVword: book(2) + chapter(3) + verse(3)  e.g. 40001001 = Matthew 1:1
#
# Run once on hilarious_marcupial before the first full-Matthew decode:
#   bash tools/download_morphgnt.sh
#
# Then pass to the driver:
#   python3 ggsd.py --verse "Matthew 1:1" --model ollama/... --morphgnt tools/sblgnt/Matthew-morphgnt.txt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$SCRIPT_DIR/sblgnt"
mkdir -p "$DEST"

BASE="https://raw.githubusercontent.com/morphgnt/sblgnt/master"

# Files live in the root of the repo (not a subdirectory).
# Book numbering in this repo: Matthew = 61 (not 40 — that is the standard NT canon number).
# BCVword in the file still uses standard NT book numbers: Matthew lines start with 40.
BOOKS=(
    "61-Mt-morphgnt.txt:Matthew-morphgnt.txt"
    "62-Mk-morphgnt.txt:Mark-morphgnt.txt"
    "63-Lk-morphgnt.txt:Luke-morphgnt.txt"
    "64-Jn-morphgnt.txt:John-morphgnt.txt"
    "65-Ac-morphgnt.txt:Acts-morphgnt.txt"
    "66-Ro-morphgnt.txt:Romans-morphgnt.txt"
    "67-1Co-morphgnt.txt:1Corinthians-morphgnt.txt"
    "68-2Co-morphgnt.txt:2Corinthians-morphgnt.txt"
)

for entry in "${BOOKS[@]}"; do
    src="${entry%%:*}"
    dst="${entry##*:}"
    if [[ -f "$DEST/$dst" ]]; then
        echo "already present: $dst"
        continue
    fi
    echo -n "downloading $dst ... "
    curl -sf "$BASE/$src" -o "$DEST/$dst" && echo "ok" || echo "FAILED (check URL: $BASE/$src)"
done

echo ""
echo "MorphGNT files in $DEST:"
ls -lh "$DEST/"

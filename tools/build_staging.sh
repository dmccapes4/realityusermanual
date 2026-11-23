#!/usr/bin/env bash
# Build all web assets and stage them for deployment.
# Run without sudo — this is the agent step.
# Usage: bash tools/build_staging.sh
set -uo pipefail   # no -e: we track failures manually and continue

REPO="$(cd "$(dirname "$0")/.." && pwd)"
WEB="$REPO/web"
STAGING="$WEB/staging"
PY="$REPO/.venv/bin/python"
LIVE="/var/www/realityusermanual"

if [[ ! -x "$PY" ]]; then
  echo "ERROR: venv not found at $PY"
  exit 1
fi

mkdir -p "$STAGING"

FAILURES=()

run() {
  local label="$1"; shift
  echo "── build: $label ──────────────────────────────────────────────────"
  if "$@"; then
    echo "  ✓ $label"
  else
    echo "  ✗ $label FAILED (continuing)"
    FAILURES+=("$label")
  fi
}

run "desks"         $PY "$REPO/tools/build_desks.py"
run "listen desk"   $PY "$REPO/tools/build_listen_desk.py"
run "phase 2 pages" $PY "$REPO/tools/build_phase2_page_web.py" -08 -09 -25 -26 -31 -35 -36
run "book plate"    $PY "$REPO/tools/book_cover_plate.py"
run "pre-phase book" $PY "$REPO/tools/build_prephase_book.py" build

if (( ${#FAILURES[@]} > 0 )); then
  echo ""
  echo "  ⚠ Build failures: ${FAILURES[*]}"
  echo "  Likely cause: root-owned files in web/ from a previous sudo deploy."
  echo "  Fix: sudo chown -R dylanmccapes:dylanmccapes $WEB/"
  echo ""
fi

echo "── stage: rsync web/ → web/staging/ ─────────────────────────────────"
rsync -a --delete \
  --exclude 'staging/' \
  --exclude 'deploy/' \
  --exclude '*.request.json' \
  "$WEB/" "$STAGING/"

echo ""
echo "── diff: staging vs. live ────────────────────────────────────────────"
if [[ -d "$LIVE" ]]; then
  DIFF=$(rsync -ain --delete \
    --exclude '*.request.json' \
    "$STAGING/" "$LIVE/" 2>/dev/null || true)
  if [[ -z "$DIFF" ]]; then
    echo "  No changes — staging matches live."
  else
    echo "$DIFF" | head -60
    N=$(echo "$DIFF" | wc -l)
    if (( N > 60 )); then echo "  … and $((N-60)) more lines"; fi
  fi
else
  echo "  (live server not mounted — diff skipped)"
fi

echo ""
echo "  Staging: $STAGING"
echo "  To go live:"
echo ""
echo "    sudo bash $REPO/web/deploy/push.sh"
echo ""

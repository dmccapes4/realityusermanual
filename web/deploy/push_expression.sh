#!/usr/bin/env bash
# Publish the generated Expression package at dylanmccapes.systems/expression.
# Run with sudo:
#   sudo bash /home/dylanmccapes/dev/REALITY_USER_MANUAL/web/deploy/push_expression.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
SOURCE="$REPO/web/expression"
LIVE="/var/www/expression"

if [[ ! -f "$SOURCE/index.html" || ! -f "$SOURCE/media/the___bed.mp4" ]]; then
  echo "ERROR: the generated Expression package is incomplete."
  echo "Run as your normal user:"
  echo "  $REPO/.venv/bin/python $REPO/tools/build_expression_site.py"
  exit 1
fi

echo "→ syncing Expression package → $LIVE"
mkdir -p "$LIVE"
rsync -av --delete --chmod=D755,F644 "$SOURCE/" "$LIVE/"

# The main domain already serves /var/www with try_files, so no nginx change or
# reload is needed for this route.
ENV_FILE="$REPO/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

CF_TOKEN="${CLOUDFLARE_PURGE_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
CF_ZONE="${CLOUDFLARE_ZONE_ID:-dc1f7c047ed389c59b985d3e2b02340e}"

if [[ -n "$CF_TOKEN" ]]; then
  echo "→ purging Cloudflare cache"
  RESPONSE="$(curl -fsS -X POST \
    "https://api.cloudflare.com/client/v4/zones/$CF_ZONE/purge_cache" \
    -H "Authorization: Bearer $CF_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"purge_everything":true}')"
  SUCCESS="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("success", False))' <<<"$RESPONSE")"
  if [[ "$SUCCESS" != "True" ]]; then
    echo "ERROR: Cloudflare cache purge failed: $RESPONSE"
    exit 1
  fi
else
  echo "→ no Cloudflare purge token found; skipping cache purge"
fi

echo "✓ https://dylanmccapes.systems/expression/"

#!/usr/bin/env bash
# Push web/staging → /var/www/realityusermanual, reload nginx, purge Cloudflare cache.
# Run with sudo:
#   sudo bash /home/dylanmccapes/dev/REALITY_USER_MANUAL/web/deploy/push.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
STAGING="$REPO/web/staging"
LIVE="/var/www/realityusermanual"
NGINX_CONF="$REPO/web/deploy/nginx.conf"
NGINX_DEST="/etc/nginx/sites-enabled/realityusermanual.dylanmccapes.systems"

# ── preflight ──────────────────────────────────────────────────────────────
if [[ ! -d "$STAGING" ]]; then
  echo "ERROR: $STAGING not found."
  echo "       Run:  bash tools/build_staging.sh"
  exit 1
fi

if [[ ! -f "$STAGING/index.html" ]]; then
  echo "ERROR: $STAGING/index.html missing — staging looks empty."
  echo "       Run:  bash tools/build_staging.sh"
  exit 1
fi

# ── fix ownership of anything root created in web/ source tree ────────────
echo "→ fixing ownership of $REPO/web/"
chown -R "$(stat -c '%U:%G' "$REPO")" "$REPO/web/" 2>/dev/null || true

# ── rsync ──────────────────────────────────────────────────────────────────
echo "→ syncing staging → live"
mkdir -p "$LIVE"
rsync -av --delete \
  --exclude '*.request.json' \
  "$STAGING/" "$LIVE/"

# ── nginx ──────────────────────────────────────────────────────────────────
echo "→ installing nginx config"
cp "$NGINX_CONF" "$NGINX_DEST"
nginx -t
systemctl reload nginx

# ── cloudflare cache purge ─────────────────────────────────────────────────
echo "→ purging Cloudflare cache"

# Load env (non-sudo vars available to root via this path)
ENV_FILE="$REPO/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

# Use CLOUDFLARE_PURGE_TOKEN if set (needs Zone:Cache Purge permission).
# Fall back to CLOUDFLARE_API_TOKEN only if PURGE_TOKEN is absent.
CF_TOKEN="${CLOUDFLARE_PURGE_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
CF_ZONE="${CLOUDFLARE_ZONE_ID:-dc1f7c047ed389c59b985d3e2b02340e}"

if [[ -z "$CF_TOKEN" ]]; then
  echo "  WARNING: No CF token set — skipping cache purge."
  echo "  Add CLOUDFLARE_PURGE_TOKEN to $ENV_FILE (Zone:Cache Purge permission)."
else
  RESP=$(curl -s -X POST \
    "https://api.cloudflare.com/client/v4/zones/$CF_ZONE/purge_cache" \
    -H "Authorization: Bearer $CF_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"purge_everything":true}')

  SUCCESS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success','false'))" 2>/dev/null || echo "false")
  if [[ "$SUCCESS" == "True" ]]; then
    echo "  ✓ Cloudflare cache purged (all)"
  else
    echo "  ✗ CF purge response: $RESP"
    echo "  Purge manually: https://dash.cloudflare.com — Caching → Purge Everything"
  fi
fi

echo ""
echo "✓ https://realityusermanual.dylanmccapes.systems"

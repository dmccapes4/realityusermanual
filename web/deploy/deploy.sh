#!/usr/bin/env bash
# Full deploy: build → stage → rsync → nginx → CF purge.
# Run with sudo:
#   sudo bash /home/dylanmccapes/dev/REALITY_USER_MANUAL/web/deploy/deploy.sh
set -uo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
WEB="$REPO/web"
STAGING="$WEB/staging"
LIVE="/var/www/realityusermanual"
NGINX_CONF="$WEB/deploy/nginx.conf"
NGINX_DEST="/etc/nginx/sites-enabled/realityusermanual.dylanmccapes.systems"
OWNER="$(stat -c '%U' "$REPO")"

# ── fix any root-owned files left by previous sudo runs ───────────────────
echo "→ fixing ownership of $WEB/"
chown -R "$OWNER:$OWNER" "$WEB/"

# ── build (run as repo owner, not root) ───────────────────────────────────
echo "→ building staging"
sudo -u "$OWNER" bash "$REPO/tools/build_staging.sh"

# ── preflight ─────────────────────────────────────────────────────────────
if [[ ! -f "$STAGING/index.html" ]]; then
  echo "ERROR: $STAGING/index.html missing after build. Aborting."
  exit 1
fi

# ── rsync ─────────────────────────────────────────────────────────────────
echo "→ syncing staging → live"
mkdir -p "$LIVE"
rsync -av --delete \
  --exclude '*.request.json' \
  "$STAGING/" "$LIVE/"

# ── nginx ─────────────────────────────────────────────────────────────────
echo "→ installing nginx config"
cp "$NGINX_CONF" "$NGINX_DEST"
nginx -t
systemctl reload nginx

# ── cloudflare cache purge ────────────────────────────────────────────────
echo "→ purging Cloudflare cache"
ENV_FILE="$REPO/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi
CF_TOKEN="${CLOUDFLARE_PURGE_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
CF_ZONE="${CLOUDFLARE_ZONE_ID:-dc1f7c047ed389c59b985d3e2b02340e}"

if [[ -z "$CF_TOKEN" ]]; then
  echo "  WARNING: no CF token — skipping purge"
else
  RESP=$(curl -s -X POST \
    "https://api.cloudflare.com/client/v4/zones/$CF_ZONE/purge_cache" \
    -H "Authorization: Bearer $CF_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"purge_everything":true}')
  SUCCESS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success','false'))" 2>/dev/null || echo "false")
  if [[ "$SUCCESS" == "True" ]]; then
    echo "  ✓ Cloudflare cache purged"
  else
    echo "  ✗ CF purge failed: $RESP"
    echo "  Purge manually: https://dash.cloudflare.com → Caching → Purge Everything"
  fi
fi

echo ""
echo "✓ https://realityusermanual.dylanmccapes.systems"

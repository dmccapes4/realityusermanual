#!/usr/bin/env bash
# Deploy the reviewer desks to realityusermanual.dylanmccapes.systems
# Run in your Terminal (needs host sudo):
#   sudo bash /home/dylanmccapes/dev/REALITY_USER_MANUAL/web/deploy/deploy.sh
set -euo pipefail

SITE_SRC="$(cd "$(dirname "$0")/.." && pwd)"
SITE_ROOT="/var/www/realityusermanual"
NGINX_DEST="/etc/nginx/sites-enabled/realityusermanual.dylanmccapes.systems"

echo "→ assembling desks"
if [[ -x "$SITE_SRC/../.venv/bin/python" ]]; then
  "$SITE_SRC/../.venv/bin/python" "$SITE_SRC/../tools/build_desks.py"
  echo "→ assembling listen desk"
  "$SITE_SRC/../.venv/bin/python" "$SITE_SRC/../tools/build_listen_desk.py"
  echo "→ phase 2 web pages"
  "$SITE_SRC/../.venv/bin/python" "$SITE_SRC/../tools/build_phase2_page_web.py" -31 -35
fi

echo "→ syncing $SITE_SRC → $SITE_ROOT"
mkdir -p "$SITE_ROOT"
rsync -a --delete \
  --exclude deploy \
  --exclude '*.request.json' \
  "$SITE_SRC/" "$SITE_ROOT/"

echo "→ installing nginx config"
cp "$SITE_SRC/deploy/nginx.conf" "$NGINX_DEST"
nginx -t
systemctl reload nginx
echo "✓ https://realityusermanual.dylanmccapes.systems"
echo "  /m/how-to-fly/"
echo "  /m/glacial-cell/"
echo "  /m/plume-wave/"
echo "  /m/how-tos/"
echo "  /m/reality-user-manual/"
echo "  /listen/"

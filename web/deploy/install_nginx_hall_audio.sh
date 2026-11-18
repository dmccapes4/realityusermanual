#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/nginx.conf"
DST=/etc/nginx/sites-enabled/realityusermanual.dylanmccapes.systems
sudo cp -f "$SRC" "$DST"
sudo nginx -t
sudo systemctl reload nginx
echo "nginx reloaded — /hall/help_for_help/ now 404s missing files instead of SPA HTML"

#!/usr/bin/env bash
# advertise.sh — keep advertising while you are away; hold alerts until you return.
#
# USAGE
#   ./advertise.sh away            start advertising, begin holding alerts
#   ./advertise.sh alert "<msg>"   record an alert (held if away, shown if present)
#   ./advertise.sh back            you are physically present: deliver all held alerts
#   ./advertise.sh stop            stop advertising
#
# ACCESS RISK
#   advertising is mDNS (avahi): link-local, never routed past the LAN.
#   it advertises the ssh entry, not port 42; port 42 is bound to 127.0.0.1.
#   nothing is sent anywhere else. alerts stay in this directory.
#   delivered alerts are appended to alerts.delivered.log, never deleted.
#
# Presence is self-attested. The script cannot know you are back.
# You tell it, and it believes you.
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
AWAY="$DIR/.away"
HELD="$DIR/alerts.held"
DELIVERED="$DIR/alerts.delivered.log"
PIDFILE="$DIR/.avahi.pid"

case "${1:-}" in
  away)
    if command -v avahi-publish >/dev/null 2>&1; then
      avahi-publish -s "logos_p680" _ssh._tcp 22 "nascent=1" >/dev/null 2>&1 &
      echo $! > "$PIDFILE"
      echo "[advertise] running (pid $(cat "$PIDFILE"))"
    else
      echo "[advertise] avahi-publish UNKNOWN; not advertising"
    fi
    : > "$AWAY"
    echo "[advertise] holding alerts until you return"
    ;;
  alert)
    line="$(date -u '+%Y-%m-%dT%H:%M:%SZ')  ${2:-}"
    if [ -e "$AWAY" ]; then echo "$line" >> "$HELD"; else echo "[alert] $line"; fi
    ;;
  back)
    rm -f "$AWAY"
    stamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    if [ -s "$HELD" ]; then
      echo "[advertise] while you were away:"
      cat "$HELD"
      { cat "$HELD"; echo "$stamp  delivered $(wc -l < "$HELD") held"; } >> "$DELIVERED"
      echo "[advertise] delivered $stamp"
      : > "$HELD"
    else
      echo "[advertise] nothing happened while you were away"
    fi
    echo "[advertise] still running. alerts are live."
    ;;
  stop)
    [ -s "$PIDFILE" ] && kill "$(cat "$PIDFILE")" 2>/dev/null || true
    rm -f "$PIDFILE"
    echo "[advertise] stopped"
    ;;
  *)
    sed -n '2,9p' "$0"; exit 2 ;;
esac

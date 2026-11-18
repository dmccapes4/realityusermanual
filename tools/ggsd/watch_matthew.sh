#!/usr/bin/env bash
# watch_matthew.sh — monitor full Matthew decode on hilarious_marcupial (245)
#
# Run from 82 (heuristic-friction):
#   bash tools/ggsd/watch_matthew.sh
#
# Polls progress.json on 245 every 30s.
# Alerts if no update in 5 minutes (stalled or dead process).
#
# Requires SSH access to 245:
#   ssh -p 2222 dylanmccapes@104.53.183.230   (WAN via UDM forward)
#   OR
#   ssh dylanmccapes@192.168.0.245             (LAN, if on same subnet)

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
REMOTE_USER="dylanmccapes"
REMOTE_HOST_WAN="104.53.183.230"
REMOTE_PORT_WAN="2222"
REMOTE_HOST_LAN="192.168.0.245"

PROGRESS_FILE="dev/REALITY_USER_MANUAL/tools/ggsd/runs/matthew_full/progress.json"
ERRORS_FILE="dev/REALITY_USER_MANUAL/tools/ggsd/runs/matthew_full/errors.jsonl"
COMPLETED_FILE="dev/REALITY_USER_MANUAL/tools/ggsd/runs/matthew_full/completed.json"

POLL_INTERVAL=30       # seconds between polls
STALE_THRESHOLD=300    # seconds before alerting (5 min)

# ── SSH helper: try WAN first, fall back to LAN ───────────────────────────────
ssh_245() {
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
           -p "$REMOTE_PORT_WAN" "$REMOTE_USER@$REMOTE_HOST_WAN" "$@" 2>/dev/null; then
        return 0
    fi
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
        "$REMOTE_USER@$REMOTE_HOST_LAN" "$@" 2>/dev/null
}

# ── Main loop ─────────────────────────────────────────────────────────────────
echo "watch_matthew — polling hilarious_marcupial every ${POLL_INTERVAL}s"
echo "Press Ctrl+C to stop."
echo ""

last_updated=""
stale_warned=false

while true; do
    now=$(date +%s)
    timestamp=$(date '+%H:%M:%S')

    # Fetch progress.json
    if ! progress_json=$(ssh_245 "cat $PROGRESS_FILE 2>/dev/null"); then
        echo "[$timestamp]  ✗  Cannot reach 245"
        sleep "$POLL_INTERVAL"
        continue
    fi

    if [[ -z "$progress_json" ]]; then
        echo "[$timestamp]  –  progress.json not found yet (run not started?)"
        sleep "$POLL_INTERVAL"
        continue
    fi

    # Parse fields
    n_done=$(echo "$progress_json"    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('n_done',0))")
    n_total=$(echo "$progress_json"   | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('n_total',1071))")
    n_words=$(echo "$progress_json"   | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('n_words_done',0))")
    current=$(echo "$progress_json"   | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('current_verse') or '-')")
    rate=$(echo "$progress_json"      | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('rate_verses_per_hour') or '-')")
    eta=$(echo "$progress_json"       | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('eta_hours') or '-')")
    status=$(echo "$progress_json"    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status','?'))")
    updated=$(echo "$progress_json"   | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('updated_utc') or '')")

    # Stale check
    if [[ -n "$updated" ]]; then
        updated_epoch=$(date -d "$updated" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$updated" +%s 2>/dev/null || echo 0)
        age=$(( now - updated_epoch ))
        if (( age > STALE_THRESHOLD )) && [[ "$status" == "running" ]]; then
            stale_label="  ⚠ STALE (${age}s since update)"
            stale_warned=true
        else
            stale_label=""
            stale_warned=false
        fi
    else
        stale_label=""
        age=0
    fi

    # Count errors
    error_count=$(ssh_245 "wc -l < $ERRORS_FILE 2>/dev/null || echo 0" | tr -d ' ')

    # Progress bar (40 chars)
    pct=$(( n_done * 40 / n_total ))
    bar=$(printf '%0.s█' $(seq 1 $pct))$(printf '%0.s░' $(seq 1 $(( 40 - pct ))))
    pct_num=$(( n_done * 100 / n_total ))

    echo "[$timestamp]  ${bar}  ${n_done}/${n_total} (${pct_num}%)  words=${n_words}  rate=${rate}v/h  ETA=${eta}h  status=${status}${stale_label}"
    echo "             current=${current}  errors=${error_count}  updated=${updated}"

    # On complete, stop polling
    if [[ "$status" == "complete" ]]; then
        echo ""
        echo "  ✓ Matthew decode complete — ${n_done} verses, ${n_words} words"
        echo "  Results: ~/dev/REALITY_USER_MANUAL/tools/ggsd/runs/Matthew_*/"
        break
    fi

    # On interrupted, note it
    if [[ "$status" == "interrupted" ]]; then
        echo "  ⚠  Process was interrupted at ${current}. Resume with same command on 245."
    fi

    sleep "$POLL_INTERVAL"
done

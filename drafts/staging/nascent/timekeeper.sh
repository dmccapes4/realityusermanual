#!/usr/bin/env bash
# timekeeper.sh — wake on BUS and write the time it woke to session.jsonl.
#
# USAGE
#   ./timekeeper.sh &              wake once per BUS tick until stopped
#   ./timekeeper.sh once           wake once, now, and write it
#   kill %1                        stop; it finishes the tick it is sleeping
#
# ACCESS RISK
#   writes only ./session.jsonl. reads only the system clock. no network.
#   append-only: a line, once written, is never changed.
#
# BUS is the only clock that matters. The timekeeper is woken by BUS, and when
# it wakes it reads the system clock and writes down what it says. Tick n is
# owed at start + n/BUS_HZ; the clock says when it came; the difference is the
# drift. Drift is recorded, never corrected. That is how the system knows what
# time is. A single wake has no BUS reference, so its drift is null: UNKNOWN.
#
# A line cannot hold its own completion, so the next line receipts it:
#   prev_write_us  how long the previous line took to write (wake -> appended)
#   wake_over_us   how late this wake came after the previous line was done + 1/BUS_HZ
# The two are the parts of the drift: the cost of writing and the cost of waking.
# Slot 0 names the keeper the clock readings come from, as it said at start.
set -e

BUS_HZ=1                               # must equal BUS_HZ in deps.c

DIR="$(cd "$(dirname "$0")" && pwd)"
LEDGER="$DIR/session.jsonl"
PIDFILE="$DIR/.timekeeper.pid"

keeper() {  # who the clock readings come from, as the keeper reports itself
    local src ref="UNKNOWN" stratum=null freq=null offs=null delay=null disp=null
    src=$(cat /sys/devices/system/clocksource/clocksource0/current_clocksource 2>/dev/null || echo UNKNOWN)
    if command -v chronyc >/dev/null 2>&1; then
        # chronyc -c tracking: refid,refname,stratum,reftime,system_offset,last_offset,rms,freq_ppm(neg=slow),resid,skew,root_delay,root_dispersion,...
        IFS=, read -r _ ref stratum _ offs _ _ freq _ _ delay disp _ < <(chronyc -c tracking 2>/dev/null) || true
    fi
    printf '"keeper":{"clocksource":"%s","ref":"%s","stratum":%s,"freq_ppm":%s,"offset_s":%s,"root_delay_s":%s,"root_dispersion_s":%s}' \
        "$src" "${ref:-UNKNOWN}" "${stratum:-null}" "${freq:-null}" "${offs:-null}" "${delay:-null}" "${disp:-null}"
}

prev_wake_us="" prev_done_us=""
write_wake() {
    local tick=$1 owed_ns=$2 woke_ns iso off drift pw=null wo=null done_us
    woke_ns=$(date +%s%N)
    if [ -n "$owed_ns" ]; then drift=$(( (woke_ns - owed_ns) / 1000000 )); else owed_ns=null; drift=null; fi
    if [ -n "$prev_done_us" ]; then
        pw=$(( prev_done_us - prev_wake_us ))
        wo=$(( woke_ns / 1000 - prev_done_us - 1000000 / BUS_HZ ))
    fi
    iso=$(date -u -d "@${woke_ns:0:-9}" '+%Y-%m-%dT%H:%M:%SZ')
    if [ ! -s "$LEDGER" ]; then
        printf '{"slot":0,"file":"session.jsonl","host":"%s","path":"%s","bus_hz":%s,%s,"describes":"one wake per line: the BUS tick, when BUS owed it, when the system clock says it woke, the drift between them in ms, the previous line'"'"'s write cost and this wake'"'"'s lateness in us, off. off is the byte offset of the line. offset 0 is this line. no wake lives at 0."}\n' \
            "$(hostname)" "$LEDGER" "$BUS_HZ" "$(keeper)" > "$LEDGER"
    fi
    off=$(stat -c %s "$LEDGER")
    printf '{"bus_tick":%s,"woke":"%s","owed_ns":%s,"woke_ns":%s,"drift_ms":%s,"prev_write_us":%s,"wake_over_us":%s,"off":%s}\n' \
        "$tick" "$iso" "$owed_ns" "$woke_ns" "$drift" "$pw" "$wo" "$off" >> "$LEDGER"
    echo "[timekeeper] tick $tick  woke $iso  drift ${drift} ms  off $off"
    done_us=${EPOCHREALTIME/./}
    prev_wake_us=$(( woke_ns / 1000 )) prev_done_us=$done_us
}

if [ "${1:-}" = "once" ]; then
    write_wake 0 ""
    exit 0
fi

if [ -s "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[timekeeper] already awake (pid $(cat "$PIDFILE"))" >&2; exit 1
fi
echo $$ > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
trap 'exit 0' TERM INT

start_ns=$(date +%s%N)
tick=0
while :; do
    sleep "$(( 1 / BUS_HZ ))"
    tick=$(( tick + 1 ))
    write_wake "$tick" $(( start_ns + tick * 1000000000 / BUS_HZ ))
done

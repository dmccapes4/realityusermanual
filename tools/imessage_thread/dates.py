"""Resolve iMessage date pills against capture_assumption_date (0b, 1a)."""

from __future__ import annotations

import datetime
import re
from zoneinfo import ZoneInfo

DATE_PILL_RE = re.compile(
    r"^(Yesterday|Today)\s+(\d{1,2}):(\d{2})\s*(AM|PM)$",
    re.I,
)
WEEKDAY_PILL_RE = re.compile(
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+"
    r"(\d{1,2}):(\d{2})\s*(AM|PM)$",
    re.I,
)

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _parse_time(h: int, m: int, ampm: str) -> tuple[int, int]:
    ampm = ampm.upper()
    if ampm == "PM" and h != 12:
        h += 12
    if ampm == "AM" and h == 12:
        h = 0
    return h, m


def resolve_pill(
    raw: str,
    capture_date: datetime.date,
    tz: ZoneInfo,
) -> tuple[str | None, str]:
    raw = raw.strip()
    m = DATE_PILL_RE.match(raw)
    if m:
        rel, hh, mm, ap = m.groups()
        hour, minute = _parse_time(int(hh), int(mm), ap)
        if rel.lower() == "today":
            d = capture_date
        else:
            d = capture_date - datetime.timedelta(days=1)
        dt = datetime.datetime(d.year, d.month, d.day, hour, minute, tzinfo=tz)
        return dt.isoformat(), "medium"

    m = WEEKDAY_PILL_RE.match(raw)
    if m:
        wd_name, hh, mm, ap = m.groups()
        target = WEEKDAYS[wd_name.lower()]
        hour, minute = _parse_time(int(hh), int(mm), ap)
        d = capture_date
        while d.weekday() != target:
            d -= datetime.timedelta(days=1)
        dt = datetime.datetime(d.year, d.month, d.day, hour, minute, tzinfo=tz)
        return dt.isoformat(), "low" if wd_name else "medium"

    return None, "low"


def resolve_thread_anchor(
    markers_raw: str,
    capture_assumption_date: str,
    tz_name: str,
) -> dict | None:
    if not markers_raw.strip():
        return None
    tz = ZoneInfo(tz_name)
    y, mo, d = (int(x) for x in capture_assumption_date.split("-"))
    capture_date = datetime.date(y, mo, d)
    first_line = markers_raw.strip().splitlines()[0].strip()
    # pill lines are often centered alone
    iso, conf = resolve_pill(first_line, capture_date, tz)
    if iso is None:
        # try to find first pill substring
        for line in markers_raw.splitlines():
            line = line.strip()
            for pattern in (DATE_PILL_RE, WEEKDAY_PILL_RE):
                m = pattern.match(line)
                if m:
                    iso, conf = resolve_pill(line, capture_date, tz)
                    first_line = line
                    break
            if iso:
                break
    if iso is None:
        return {"raw": first_line, "timestamp_iso": None, "timestamp_confidence": "low"}
    return {
        "raw": first_line,
        "timestamp_iso": iso,
        "timestamp_confidence": conf,
    }


def process_date_default(explicit: str) -> str:
    if explicit:
        return explicit
    return datetime.date.today().isoformat()

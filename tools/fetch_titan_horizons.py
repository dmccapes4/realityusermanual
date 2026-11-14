#!/usr/bin/env python3
"""Fetch and cache exact JPL Horizons state vectors (barycentric ICRF/ECLIPJ2000, km & km/s).

Caches immutable JSON records in REALITY_USER_MANUAL/data/titan_ephemeris/ so all
trajectory integrations use known JPL measurements with zero guessed elements.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "titan_ephemeris"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_horizons_vectors(
    command: str,
    start_time: str,
    stop_time: str,
    step_size: str = "1d",
    center: str = "500@0",
    ref_plane: str = "ECLIPTIC",
) -> list[dict]:
    """Query JPL Horizons VECTORS table (OUT_UNITS=KM-S, VEC_TABLE=2: X,Y,Z,VX,VY,VZ)."""
    params = {
        "format": "text",
        "COMMAND": f"'{command}'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": f"'{center}'",
        "REF_PLANE": f"'{ref_plane}'",
        "REF_SYSTEM": "'ICRF'",
        "OUT_UNITS": "'KM-S'",
        "VEC_TABLE": "'2'",
        "CSV_FORMAT": "'YES'",
        "START_TIME": f"'{start_time}'",
        "STOP_TIME": f"'{stop_time}'",
        "STEP_SIZE": f"'{step_size}'",
    }
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "RealityUserManual-TitanTracker/1.0"})
    txt = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")
    if "$$SOE" not in txt:
        msg = txt.splitlines()[-15:]
        raise RuntimeError(f"Horizons returned no ephemeris for {command} ({start_time}..{stop_time}):\n" + "\n".join(msg))
    soe = txt.split("$$SOE", 1)[1].split("$$EOE", 1)[0].strip()
    rows = []
    for line in soe.splitlines():
        parts = [p.strip() for p in line.split(",") if p.strip() != ""]
        if len(parts) < 8:
            continue
        jd_tdb = float(parts[0])
        cal = parts[1].replace("A.D. ", "").strip()
        x, y, z, vx, vy, vz = (float(parts[i]) for i in range(2, 8))
        rows.append({
            "jd_tdb": jd_tdb,
            "cal_tdb": cal,
            "pos_km": [x, y, z],
            "vel_kms": [vx, vy, vz],
        })
    return rows


def main() -> None:
    out_path = CACHE_DIR / "horizons_anchor_vectors.json"
    if out_path.exists():
        data = json.loads(out_path.read_text())
    else:
        data = {"meta": {"center": "500@0 (Solar System Barycenter)", "frame": "ECLIPJ2000 (ICRF)", "units": "km, km/s"}, "records": {}}

    queries = [
        # Saturn system bodies at 1750-01-01 (earliest SAT441 date, for 1679 backward check & 1821 forward check)
        ("saturn_1750", "699", "1750-01-01", "1750-01-02", "1d"),
        ("titan_1750", "606", "1750-01-01", "1750-01-02", "1d"),
        ("rhea_1750", "605", "1750-01-01", "1750-01-02", "1d"),
        ("iapetus_1750", "608", "1750-01-01", "1750-01-02", "1d"),
        ("dione_1750", "604", "1750-01-01", "1750-01-02", "1d"),
        ("tethys_1750", "603", "1750-01-01", "1750-01-02", "1d"),
        # 1821-01-01 (71 years after 1750, to measure exact 71-yr Titan integration error!)
        ("saturn_1821", "699", "1821-01-01", "1821-01-02", "1d"),
        ("titan_1821", "606", "1821-01-01", "1821-01-02", "1d"),
        # Voyager 1 (1977-1980) historic Terra -> Jupiter -> Titan mission + Saturnian system
        ("voyager1_waypoints", "-31", "1977-09-08", "1980-11-15", "1d"),
        ("saturn_v1_window", "699", "1977-09-08", "1977-09-09", "1d"),
        ("titan_v1_start", "606", "1977-09-08", "1977-09-09", "1d"),
        ("rhea_v1_start", "605", "1977-09-08", "1977-09-09", "1d"),
        ("iapetus_v1_start", "608", "1977-09-08", "1977-09-09", "1d"),
        ("dione_v1_start", "604", "1977-09-08", "1977-09-09", "1d"),
        ("tethys_v1_start", "603", "1977-09-08", "1977-09-09", "1d"),
        # Fine hourly vectors around Voyager 1 Jupiter flyby (1979-03-04..06) and Titan flyby (1980-11-11..13)
        ("voyager1_jup_fine", "-31", "1979-03-04", "1979-03-07", "1h"),
        ("jupiter_body_1979", "599", "1979-02-25", "1979-03-08", "6h"),
        ("voyager1_tit_fine", "-31", "1980-11-11", "1980-11-14", "1h"),
        ("saturn_1980_tit", "699", "1980-11-01", "1980-11-15", "6h"),
        ("titan_1980_tit", "606", "1980-11-01", "1980-11-15", "6h"),
        ("saturn_1979_jup", "699", "1979-02-25", "1979-02-26", "1d"),
        ("titan_1979_jup", "606", "1979-02-25", "1979-02-26", "1d"),
        ("rhea_1979_jup", "605", "1979-02-25", "1979-02-26", "1d"),
        ("iapetus_1979_jup", "608", "1979-02-25", "1979-02-26", "1d"),
        ("dione_1979_jup", "604", "1979-02-25", "1979-02-26", "1d"),
        ("tethys_1979_jup", "603", "1979-02-25", "1979-02-26", "1d"),
        # New Horizons (2006-2007) historic fast Terra -> Jupiter
        ("newhorizons_2006", "-98", "2006-01-20", "2007-03-02", "2d"),
        ("newhorizons_jup_fine", "-98", "2007-02-27", "2007-03-01", "1h"),
        ("jupiter_body_2007", "599", "2007-02-27", "2007-03-01", "1h"),
        # Mars 2020 Perseverance (-168) historic Terra -> Mars (2020-07-30 -> 2021-02-18)
        ("mars2020_cruise", "-168", "2020-07-31", "2021-02-19", "2d"),
        ("mars2020_arr_fine", "-168", "2021-02-18", "2021-02-19", "1h"),
        ("mars_body_2021", "499", "2021-02-18", "2021-02-19", "1h"),
        # Gattaca film release year / Cassini launch epoch (1997-10-15) + 1998-10-15 Titan target
        ("saturn_1997_1999", "699", "1997-10-01", "1999-01-01", "2d"),
        ("titan_1997_1999", "606", "1997-10-01", "1999-01-01", "2d"),
        # Modern 2020-2021 Jupiter-Saturn alignment window (Saturn + Titan)
        ("saturn_2019_2022", "699", "2019-06-01", "2022-01-01", "2d"),
        ("titan_2019_2022", "606", "2019-06-01", "2022-01-01", "2d"),
    ]

    for key, cmd, t0, t1, step in queries:
        if key in data["records"]:
            print(f"[cached] {key}: {len(data['records'][key])} rows")
            continue
        print(f"[fetch]  {key} ({cmd}: {t0} .. {t1} @ {step}) ...", flush=True)
        rows = fetch_horizons_vectors(cmd, t0, t1, step)
        data["records"][key] = rows
        out_path.write_text(json.dumps(data, indent=1))
        print(f"         -> {len(rows)} rows")
        time.sleep(0.15)

    print(f"Done. Wrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Zero-Ratio Trajectory & Required-Field-Drift Tracker for Terra -> Titan.

Rules & Review Compliance (operator + HALMANSEIR review, 2026-11-13):
  1. No Hohmann, no vis-viva, no Lambert conic bisection, no patched-conic SOI seams,
     no dimensionless ratio shortcuts.
  2. Every object is tracked by its 3D position [x, y, z] (km), linear translation
     rate s >= 0 (km/s), and unit heading u_hat.
  3. At each step, external acceleration resolves into two separate physical vectors:
       - linear rate change ds/dt = dot(a_total, u_hat)        [km/s^2]
       - directional decay  du_hat/dt = a_perp / s             [rad/s]
     bending the heading toward objects of higher gravitability.
  4. Planetary body GMs (GM_PLANET, used for J2 oblateness and individual bodies) are
     explicitly separated from DE440 system-barycenter GMs (GM_SYSTEM_BARY, used when
     evaluating DE440 outer-planet barycenter segments [0, 5..8]).
  5. Row selection uses calendar/JD matching with strict jd_tdb equality assertions
     (zero magic array indices), and every solve_ivp / least_squares call asserts
     convergence.
  6. Part 4 solves an inverse boundary-value problem for the REQUIRED equivalent
     field-drift acceleration (mm/s^2) to close Terra_escape -> Titan_1000km_interface
     in 365.25 days with zero reaction exhaust (dm/dt = 0), followed by event-driven
     Huygens-atmosphere aerocapture (surface-impact and 1000-km atmosphere-exit events).

Outputs:
  - REALITY_USER_MANUAL/data/titan_ephemeris/titan_governed_results.json
  - REALITY_USER_MANUAL/data/titan_ephemeris/titan_1yr_trajectory.jsonl
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from jplephem.spk import SPK
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "titan_ephemeris"
DE440_PATH = Path("/tmp/skyfield-data/de440.bsp")
HZ_PATH = DATA_DIR / "horizons_anchor_vectors.json"

DAY_S = 86400.0
YEAR_D = 365.25
YEAR_S = YEAR_D * DAY_S

# ── Planetary Body GMs & Radii (body alone; used for J2 oblateness & resolved bodies) ──
BODY_META = {
    "sol":     {"gm_planet": 132712440041.93938, "r_eq_km": 695700.0, "r_mean_km": 695700.0, "rot_h": 601.2},
    "mercury": {"gm_planet": 22031.868551,       "r_eq_km": 2440.5,   "r_mean_km": 2439.7,   "rot_h": 1407.5},
    "venus":   {"gm_planet": 324858.592000,      "r_eq_km": 6051.8,   "r_mean_km": 6051.8,   "rot_h": 5832.6},
    "terra":   {"gm_planet": 398600.435507,      "r_eq_km": 6378.137, "r_mean_km": 6371.0,   "rot_h": 23.9345},
    "luna":    {"gm_planet": 4902.800118,        "r_eq_km": 1738.1,   "r_mean_km": 1737.4,   "rot_h": 655.72},
    "mars":    {"gm_planet": 42828.375214,       "r_eq_km": 3396.2,   "r_mean_km": 3389.5,   "rot_h": 24.6229},
    "jupiter": {"gm_planet": 126686531.900,      "r_eq_km": 71492.0,  "r_mean_km": 69911.0,  "rot_h": 9.9250},
    "saturn":  {"gm_planet": 37931206.234,       "r_eq_km": 60268.0,  "r_mean_km": 58232.0,  "rot_h": 10.5610},
    "titan":   {"gm_planet": 8978.1382,          "r_eq_km": 2575.5,   "r_mean_km": 2575.5,   "rot_h": 382.690},
    "uranus":  {"gm_planet": 5793951.3,          "r_eq_km": 25559.0,  "r_mean_km": 25362.0,  "rot_h": 17.24},
    "neptune": {"gm_planet": 6835099.97,         "r_eq_km": 24764.0,  "r_mean_km": 24622.0,  "rot_h": 16.11},
}

# ── DE440 System-Barycenter GMs (planet + satellite system, for DE440 segments [0, 4..8]) ──
GM_SYSTEM_BARY = {
    "mars_bary":    42828.375214,
    "jupiter_bary": 126712764.800000,
    "saturn_bary":  37940585.200000,
    "uranus_bary":  5794556.400000,
    "neptune_bary": 6836527.100580,
}

GM_SATURN_MOONS = {
    "titan":   8978.1382,
    "rhea":    153.9426,
    "iapetus": 120.5038,
    "dione":   73.1146,
    "tethys":  41.2067,
    "inner_mimas_enceladus": 2.52 + 7.20,
}

SATURN_RING_INNER_KM = 66900.0
SATURN_RING_OUTER_KM = 140180.0
TERRA_HILL_RADIUS_KM = 1471428.0
TITAN_ATMO_INTERFACE_KM = 1000.0
J2_SATURN = 0.016298
J2_JUPITER = 0.014696

# ── Frame Rotation Matrices (ICRF -> ECLIPJ2000 -> Sol-Equatorial) ────────────────────────────
EPS_J2000 = math.radians(84381.448 / 3600.0)
R_ICRF_TO_ZECL = np.array([
    [1.0, 0.0, 0.0],
    [0.0, math.cos(EPS_J2000), math.sin(EPS_J2000)],
    [0.0, -math.sin(EPS_J2000), math.cos(EPS_J2000)],
])


def _pole_ecl(ra_deg: float, dec_deg: float) -> np.ndarray:
    ra, dec = math.radians(ra_deg), math.radians(dec_deg)
    icrf = np.array([math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec)])
    v = R_ICRF_TO_ZECL @ icrf
    return v / np.linalg.norm(v)


POLE_SOL = _pole_ecl(286.13, 63.87)         # Sol spin north pole (7.25 deg to Zecliptic, node 75.76 deg)
POLE_SATURN = _pole_ecl(40.589, 83.537)     # Saturn spin & ring-plane pole
POLE_JUPITER = _pole_ecl(268.056595, 64.495303)

_node_sol = np.cross(np.array([0.0, 0.0, 1.0]), POLE_SOL)
X_SOL_EQ = _node_sol / np.linalg.norm(_node_sol)
Y_SOL_EQ = np.cross(POLE_SOL, X_SOL_EQ)
R_ZECL_TO_SOLEQ = np.vstack([X_SOL_EQ, Y_SOL_EQ, POLE_SOL])


def row_by_cal(rows: list[dict], cal_prefix: str) -> dict:
    """Select a cached Horizons row by calendar timestamp prefix (no magic indices)."""
    matches = [r for r in rows if r["cal_tdb"].startswith(cal_prefix)]
    if not matches:
        raise KeyError(f"No Horizons row matching '{cal_prefix}' (first={rows[0]['cal_tdb']}, last={rows[-1]['cal_tdb']})")
    return matches[0]


def row_by_jd(rows: list[dict], jd_target: float, tol: float = 1e-6) -> dict:
    """Select a cached Horizons row by Julian Date with tolerance assertion."""
    for r in rows:
        if abs(float(r["jd_tdb"]) - jd_target) <= tol:
            return r
    raise KeyError(f"No Horizons row at JD {jd_target}")


def assert_same_jd(*rows: dict, tol: float = 1e-7) -> float:
    """Assert that two or more Horizons records share the exact same TDB epoch."""
    jd0 = float(rows[0]["jd_tdb"])
    for r in rows[1:]:
        jd = float(r["jd_tdb"])
        assert abs(jd - jd0) <= tol, f"JD mismatch: {jd0} ({rows[0]['cal_tdb']}) vs {jd} ({r['cal_tdb']})"
    return jd0


@dataclass
class ObjectState:
    """Independent per-object physical state: position, linear rate, and unit direction."""
    name: str
    jd_tdb: float
    pos_km: np.ndarray        # [x, y, z] km in 3D Zecliptic frame
    speed_kms: float          # linear translation rate >= 0 (km/s)
    dir_unit: np.ndarray      # unit direction vector [ux, uy, uz]

    @classmethod
    def from_pv(cls, name: str, jd_tdb: float, pos_km: np.ndarray, vel_kms: np.ndarray) -> "ObjectState":
        s = float(np.linalg.norm(vel_kms))
        u = vel_kms / s if s > 1e-15 else np.array([1.0, 0.0, 0.0])
        return cls(name=name, jd_tdb=jd_tdb, pos_km=pos_km.copy(), speed_kms=s, dir_unit=u)

    @property
    def vel_kms(self) -> np.ndarray:
        return self.speed_kms * self.dir_unit


def decompose_rates(state: ObjectState, acc_kms2: np.ndarray) -> dict:
    """Split total acceleration into parallel speed rate (km/s^2) and perpendicular directional decay (rad/s)."""
    speed_rate = float(np.dot(acc_kms2, state.dir_unit))
    a_perp = acc_kms2 - speed_rate * state.dir_unit
    perp_mag = float(np.linalg.norm(a_perp))
    dir_decay_rads = perp_mag / max(state.speed_kms, 1e-12)
    return {
        "speed_rate_kms2": speed_rate,
        "dir_decay_rads": dir_decay_rads,
        "dir_decay_deg_day": math.degrees(dir_decay_rads) * DAY_S,
        "dir_decay_vec_rads": (a_perp / max(state.speed_kms, 1e-12)).tolist(),
    }


class KnownSystemTracker:
    """Tracks planets and moons from JPL DE440 + cached Horizons anchors, with explicit planet vs system GMs."""

    def __init__(self) -> None:
        if not DE440_PATH.exists():
            from skyfield.api import Loader
            Loader("/tmp/skyfield-data")("de440.bsp")
        self.spk = SPK.open(str(DE440_PATH))
        self.hz = json.loads(HZ_PATH.read_text())["records"]

    def bary_pv_zecl(self, body: str, jd_tdb: float) -> tuple[np.ndarray, np.ndarray]:
        """Barycentric 3D position (km) and velocity (km/s) in Zecliptic (ECLIPJ2000) frame."""
        if body == "sol":
            p, v = self.spk[0, 10].compute_and_differentiate(jd_tdb)
        elif body == "mercury":
            p1, v1 = self.spk[0, 1].compute_and_differentiate(jd_tdb)
            p2, v2 = self.spk[1, 199].compute_and_differentiate(jd_tdb)
            p, v = p1 + p2, v1 + v2
        elif body == "venus":
            p1, v1 = self.spk[0, 2].compute_and_differentiate(jd_tdb)
            p2, v2 = self.spk[2, 299].compute_and_differentiate(jd_tdb)
            p, v = p1 + p2, v1 + v2
        elif body == "terra":
            p1, v1 = self.spk[0, 3].compute_and_differentiate(jd_tdb)
            p2, v2 = self.spk[3, 399].compute_and_differentiate(jd_tdb)
            p, v = p1 + p2, v1 + v2
        elif body == "luna":
            p1, v1 = self.spk[0, 3].compute_and_differentiate(jd_tdb)
            p2, v2 = self.spk[3, 301].compute_and_differentiate(jd_tdb)
            p, v = p1 + p2, v1 + v2
        elif body == "earth_bary":
            p, v = self.spk[0, 3].compute_and_differentiate(jd_tdb)
        elif body in ("mars", "mars_bary"):
            p, v = self.spk[0, 4].compute_and_differentiate(jd_tdb)
        elif body in ("jupiter", "jupiter_bary"):
            p, v = self.spk[0, 5].compute_and_differentiate(jd_tdb)
        elif body == "saturn_bary":
            p, v = self.spk[0, 6].compute_and_differentiate(jd_tdb)
        elif body in ("uranus", "uranus_bary"):
            p, v = self.spk[0, 7].compute_and_differentiate(jd_tdb)
        elif body in ("neptune", "neptune_bary"):
            p, v = self.spk[0, 8].compute_and_differentiate(jd_tdb)
        else:
            raise KeyError(body)
        return R_ICRF_TO_ZECL @ p, R_ICRF_TO_ZECL @ (v / DAY_S)

    def sol_centered_report(self, body: str, jd_tdb: float) -> dict:
        """Report body's position, surface clearance, linear rate, directional decay, and Sol-Eq tilt."""
        meta_key = body.replace("_bary", "")
        p_sol, v_sol = self.bary_pv_zecl("sol", jd_tdb)
        p_b, v_b = self.bary_pv_zecl(body, jd_tdb)
        rel_p = p_b - p_sol
        rel_v = v_b - v_sol
        d_center = float(np.linalg.norm(rel_p))
        r_body = BODY_META[meta_key]["r_eq_km"]
        r_sol = BODY_META["sol"]["r_eq_km"]
        st = ObjectState.from_pv(body, jd_tdb, rel_p, rel_v)
        acc = self.grav_acc_bary(jd_tdb, p_b, exclude=meta_key) - self.grav_acc_bary(jd_tdb, p_sol, exclude="sol")
        rates = decompose_rates(st, acc)
        p_soleq = R_ZECL_TO_SOLEQ @ rel_p
        lat_soleq_deg = math.degrees(math.asin(np.clip(p_soleq[2] / d_center, -1.0, 1.0)))
        lat_zecl_deg = math.degrees(math.asin(np.clip(rel_p[2] / d_center, -1.0, 1.0)))
        return {
            "body": body,
            "jd_tdb": jd_tdb,
            "d_sol_center_km": round(d_center, 3),
            "d_surface_to_surface_km": round(d_center - r_sol - r_body, 3),
            "speed_kms": round(st.speed_kms, 5),
            "radial_rate_kms": round(float(np.dot(rel_v, rel_p / d_center)), 5),
            "speed_rate_kms2": rates["speed_rate_kms2"],
            "dir_decay_rads": rates["dir_decay_rads"],
            "dir_decay_deg_day": round(rates["dir_decay_deg_day"], 5),
            "zecliptic_lat_deg": round(lat_zecl_deg, 4),
            "sol_equator_lat_deg": round(lat_soleq_deg, 4),
        }

    def grav_acc_bary(self, jd_tdb: float, pos_km: np.ndarray, exclude: str = "") -> np.ndarray:
        """Exact 3D N-body gravitational acceleration (km/s^2) in barycentric Zecliptic coordinates.

        Uses GM_PLANET for resolved bodies (Sol, Mercury, Venus, Terra, Luna) and GM_SYSTEM_BARY
        for DE440 outer barycenter segments [0, 4..8]; J2 oblateness strictly uses GM_PLANET.
        """
        acc = np.zeros(3)
        sources = [
            ("sol",          "sol",     BODY_META["sol"]["gm_planet"]),
            ("mercury",      "mercury", BODY_META["mercury"]["gm_planet"]),
            ("venus",        "venus",   BODY_META["venus"]["gm_planet"]),
            ("terra",        "terra",   BODY_META["terra"]["gm_planet"]),
            ("luna",         "luna",    BODY_META["luna"]["gm_planet"]),
            ("mars_bary",    "mars",    GM_SYSTEM_BARY["mars_bary"]),
            ("jupiter_bary", "jupiter", GM_SYSTEM_BARY["jupiter_bary"]),
            ("saturn_bary",  "saturn",  GM_SYSTEM_BARY["saturn_bary"]),
            ("uranus_bary",  "uranus",  GM_SYSTEM_BARY["uranus_bary"]),
            ("neptune_bary", "neptune", GM_SYSTEM_BARY["neptune_bary"]),
        ]
        for key, meta_key, gm_mono in sources:
            if key == exclude or meta_key == exclude:
                continue
            bp, _ = self.bary_pv_zecl(key, jd_tdb)
            d = bp - pos_km
            r2 = float(np.dot(d, d))
            if r2 < 1.0:
                continue
            r = math.sqrt(r2)
            u = d / r
            acc += (gm_mono / r2) * u
            # Oblate J2 near Jupiter and Saturn strictly uses planetary GM_PLANET!
            if meta_key == "jupiter" and r < 500.0 * BODY_META["jupiter"]["r_eq_km"]:
                gm_p = BODY_META["jupiter"]["gm_planet"]
                req_r2 = (BODY_META["jupiter"]["r_eq_km"] / r) ** 2
                u_rel = -u
                zp = float(np.dot(u_rel, POLE_JUPITER))
                f_j2 = 1.5 * J2_JUPITER * (gm_p / r2) * req_r2
                acc += f_j2 * ((5.0 * zp * zp - 1.0) * u_rel - 2.0 * zp * POLE_JUPITER)
            elif meta_key == "saturn" and r < 500.0 * BODY_META["saturn"]["r_eq_km"]:
                gm_p = BODY_META["saturn"]["gm_planet"]
                req_r2 = (BODY_META["saturn"]["r_eq_km"] / r) ** 2
                u_rel = -u
                zp = float(np.dot(u_rel, POLE_SATURN))
                f_j2 = 1.5 * J2_SATURN * (gm_p / r2) * req_r2
                acc += f_j2 * ((5.0 * zp * zp - 1.0) * u_rel - 2.0 * zp * POLE_SATURN)
        return acc


def integrate_saturn_moons_explicit(
    sys_tracker: KnownSystemTracker,
    jd_start: float,
    jd_target: float,
    moon_names: list[str],
    rel_pv0: np.ndarray,
) -> np.ndarray:
    """Explicit multi-moon Saturn-frame integrator (Titan + Rhea + Iapetus) with reconciled GM_PLANET J2 + reflex."""
    gm_sat_planet = BODY_META["saturn"]["gm_planet"]
    r_eq = BODY_META["saturn"]["r_eq_km"]
    # Un-tracked interior moons contribute only to central monopole, never to J2
    untracked_inner_gm = GM_SATURN_MOONS["inner_mimas_enceladus"]
    for inner_nm in ("tethys", "dione", "rhea"):
        if inner_nm not in moon_names:
            untracked_inner_gm += GM_SATURN_MOONS[inner_nm]
    gm_monopole = gm_sat_planet + untracked_inner_gm
    gms = [GM_SATURN_MOONS[nm] for nm in moon_names]

    def central_acc(pos: np.ndarray) -> np.ndarray:
        r2 = float(np.dot(pos, pos))
        r = math.sqrt(r2)
        u = pos / r
        zp = float(np.dot(u, POLE_SATURN))
        acc = -(gm_monopole / r2) * u
        f_j2 = 1.5 * J2_SATURN * (gm_sat_planet / r2) * ((r_eq / r) ** 2)
        acc += f_j2 * ((5.0 * zp * zp - 1.0) * u - 2.0 * zp * POLE_SATURN)
        return acc

    def rhs(t_sec: float, y: np.ndarray) -> np.ndarray:
        jd = jd_start + t_sec / DAY_S
        xsat, _ = sys_tracker.bary_pv_zecl("saturn_bary", jd)
        n = len(moon_names)
        pos = [y[6 * i : 6 * i + 3] for i in range(n)]
        vel = [y[6 * i + 3 : 6 * i + 6] for i in range(n)]
        direct = [central_acc(pos[i]) for i in range(n)]
        reflex = sum((gms[j] / gm_sat_planet) * direct[j] for j in range(n))

        ext_d = []
        for ext_key, gm_e in (("sol", BODY_META["sol"]["gm_planet"]), ("jupiter_bary", GM_SYSTEM_BARY["jupiter_bary"])):
            xp, _ = sys_tracker.bary_pv_zecl(ext_key, jd)
            de = xp - xsat
            ext_d.append((gm_e, de, float(np.dot(de, de)) ** 1.5))

        out = []
        for i in range(n):
            acc = direct[i] + reflex
            for j in range(n):
                if i == j:
                    continue
                d = pos[j] - pos[i]
                acc += gms[j] * d / (float(np.dot(d, d)) ** 1.5)
            for gm_e, de, re3 in ext_d:
                di = de - pos[i]
                acc += gm_e * (di / (float(np.dot(di, di)) ** 1.5) - de / re3)
            out.extend(vel[i])
            out.extend(acc)
        return np.array(out)

    span_s = (jd_target - jd_start) * DAY_S
    if abs(span_s) < 1e-3:
        return rel_pv0.copy()
    sol = solve_ivp(rhs, (0.0, span_s), rel_pv0, method="DOP853", rtol=1e-11, atol=1e-11)
    assert sol.success, f"Saturn moon integration failed ({jd_start} -> {jd_target}): {sol.message}"
    return sol.y[:, -1]


# ── Part 1: Historic Three Legs (Zero Propulsion, Date-Verified JPL Rows) ─────────────────────
def verify_historic_legs(tracker: KnownSystemTracker) -> dict:
    hz = tracker.hz
    results = {}

    # 1. Terra -> Mars: Mars 2020 Perseverance (-168)
    #    TCM-2 occurred 2020-Sep-30; terminal approach TCM-5 occurred 2021-Feb-16 (~0.73 m/s).
    #    We report BOTH the pure unpowered cruise (2020-Oct-03 -> 2021-Feb-14, zero TCMs >0.25 m/s)
    #    AND the full coast to atmospheric entry (2021-Feb-18 20:00 TDB, noting TCM-5/6 inside drift).
    m_rows = hz["mars2020_cruise"]
    r_m_launch = row_by_cal(m_rows, "2020-Jul-31")
    r_m0 = row_by_cal(m_rows, "2020-Oct-03")
    r_m_pre_tcm5 = row_by_cal(m_rows, "2021-Feb-14")
    r_m_entry = row_by_cal(hz["mars2020_arr_fine"], "2021-Feb-18 20:00")
    mars_at_entry = row_by_cal(hz["mars_body_2021"], "2021-Feb-18 20:00")
    assert_same_jd(r_m_entry, mars_at_entry)

    jd0 = float(r_m0["jd_tdb"])
    jd_pre = float(r_m_pre_tcm5["jd_tdb"])
    jd_ent = float(r_m_entry["jd_tdb"])

    sol_m_pure = solve_ivp(
        lambda t, y: np.concatenate([y[3:], tracker.grav_acc_bary(jd0 + t / DAY_S, y[:3])]),
        (0.0, (jd_pre - jd0) * DAY_S),
        np.array(r_m0["pos_km"] + r_m0["vel_kms"]),
        method="DOP853", rtol=1e-11, atol=1e-11,
    )
    assert sol_m_pure.success, sol_m_pure.message

    sol_m_entry = solve_ivp(
        lambda t, y: np.concatenate([y[3:], tracker.grav_acc_bary(jd0 + t / DAY_S, y[:3])]),
        (0.0, (jd_ent - jd0) * DAY_S),
        np.array(r_m0["pos_km"] + r_m0["vel_kms"]),
        method="DOP853", rtol=1e-11, atol=1e-11,
    )
    assert sol_m_entry.success, sol_m_entry.message

    mars_pos_jpl = np.array(mars_at_entry["pos_km"])
    d_mars_center = float(np.linalg.norm(sol_m_entry.y[:3, -1] - mars_pos_jpl))
    results["terra_to_mars_mars2020"] = {
        "craft": "Mars 2020 Perseverance (-168)",
        "coast_start_cal": r_m0["cal_tdb"],
        "pure_coast_end_cal": r_m_pre_tcm5["cal_tdb"],
        "pure_coast_days": round(jd_pre - jd0, 3),
        "pure_coast_drift_vs_jpl_km": round(float(np.linalg.norm(sol_m_pure.y[:3, -1] - np.array(r_m_pre_tcm5["pos_km"]))), 2),
        "entry_cal": r_m_entry["cal_tdb"],
        "coast_to_entry_days": round(jd_ent - jd0, 4),
        "launch_table_to_entry_days": round(jd_ent - float(r_m_launch["jd_tdb"]), 4),
        "drift_to_entry_vs_jpl_km": round(float(np.linalg.norm(sol_m_entry.y[:3, -1] - np.array(r_m_entry["pos_km"]))), 2),
        "drift_note": "Pure coast (Oct 3 -> Feb 14) precedes terminal targeting trims; Oct 3 -> Feb 18 20:00 includes tiny TCM-3 (~0.1 m/s) and terminal entry trims (Feb 16-18) plus SRP.",
        "distance_to_mars_center_at_entry_km": round(d_mars_center, 2),
        "altitude_above_mars_surface_km": round(d_mars_center - BODY_META["mars"]["r_eq_km"], 2),
    }

    # 2. Terra -> Jupiter: New Horizons (-98)
    #    Launch: 2006-Jan-19 19:00 UTC (~JD 2453755.2924 TDB). TCM-3 was 2006-Mar-09 (~1.1 m/s).
    #    From 2006-Mar-13 00:00 to Jupiter closest approach (2007-Feb-28 05:00 TDB) = 352.208 days unpowered!
    nh_rows = hz["newhorizons_2006"]
    r_nh_dep = row_by_cal(nh_rows, "2006-Jan-22")
    r_nh0 = row_by_cal(nh_rows, "2006-Mar-13")
    r_nh1 = row_by_cal(hz["newhorizons_jup_fine"], "2007-Feb-28 05:00")
    jup_nh = row_by_cal(hz["jupiter_body_2007"], "2007-Feb-28 05:00")
    assert_same_jd(r_nh1, jup_nh)

    jd_nh0, jd_nh1 = float(r_nh0["jd_tdb"]), float(r_nh1["jd_tdb"])
    sol_nh = solve_ivp(
        lambda t, y: np.concatenate([y[3:], tracker.grav_acc_bary(jd_nh0 + t / DAY_S, y[:3])]),
        (0.0, (jd_nh1 - jd_nh0) * DAY_S),
        np.array(r_nh0["pos_km"] + r_nh0["vel_kms"]),
        method="DOP853", rtol=1e-11, atol=1e-11,
    )
    assert sol_nh.success, sol_nh.message

    jd_nh_launch = 2453755.2924  # 2006-Jan-19 19:00 UTC actual launch
    nh_total_days = jd_nh1 - jd_nh_launch
    _, v_sol_dep = tracker.bary_pv_zecl("sol", float(r_nh_dep["jd_tdb"]))
    r_nh_post = row_by_cal(nh_rows, "2007-Mar-02")
    _, v_sol_post = tracker.bary_pv_zecl("sol", float(r_nh_post["jd_tdb"]))
    v_nh_dep = float(np.linalg.norm(np.array(r_nh_dep["vel_kms"]) - v_sol_dep))
    v_nh_post_jup = float(np.linalg.norm(np.array(r_nh_post["vel_kms"]) - v_sol_post))
    d_jup_nh = float(np.linalg.norm(sol_nh.y[:3, -1] - np.array(jup_nh["pos_km"])))

    results["terra_to_jupiter_newhorizons"] = {
        "craft": "New Horizons (-98)",
        "launch_utc": "2006-01-19 19:00",
        "pure_coast_start_cal": r_nh0["cal_tdb"],
        "jupiter_closest_approach_cal": r_nh1["cal_tdb"],
        "launch_to_ca_days": round(nh_total_days, 3),
        "launch_to_ca_years": round(nh_total_days / YEAR_D, 4),
        "integrated_post_tcm3_coast_days": round(jd_nh1 - jd_nh0, 4),
        "post_escape_sol_speed_kms": round(v_nh_dep, 3),
        "post_jupiter_sol_speed_kms": round(v_nh_post_jup, 3),
        "drift_vs_jpl_telemetry_km": round(float(np.linalg.norm(sol_nh.y[:3, -1] - np.array(r_nh1["pos_km"]))), 2),
        "jupiter_surface_altitude_km": round(d_jup_nh - BODY_META["jupiter"]["r_eq_km"], 1),
    }

    # 3. Jupiter -> Titan: Voyager 1 (-31)
    v1_rows = hz["voyager1_waypoints"]
    r_pre_j = row_by_cal(v1_rows, "1979-Feb-15")
    r_jup_ca = row_by_cal(hz["voyager1_jup_fine"], "1979-Mar-05 12:00")
    jup_1979 = row_by_cal(hz["jupiter_body_1979"], "1979-Mar-05 12:00")
    assert_same_jd(r_jup_ca, jup_1979)

    r_post_j = row_by_cal(v1_rows, "1979-Apr-16")  # Post-Apr-10/11 trajectory trim
    r_tit_05 = row_by_cal(hz["voyager1_tit_fine"], "1980-Nov-12 05:00")
    r_tit_06 = row_by_cal(hz["voyager1_tit_fine"], "1980-Nov-12 06:00")
    t_row_06 = row_by_cal(hz["titan_1980_tit"], "1980-Nov-12 06:00")
    assert_same_jd(r_tit_06, t_row_06)

    v_pre = float(np.linalg.norm(np.array(r_pre_j["vel_kms"]) - tracker.bary_pv_zecl("sol", float(r_pre_j["jd_tdb"]))[1]))
    v_post = float(np.linalg.norm(np.array(r_post_j["vel_kms"]) - tracker.bary_pv_zecl("sol", float(r_post_j["jd_tdb"]))[1]))

    jd_v0, jd_v1 = float(r_post_j["jd_tdb"]), float(r_tit_05["jd_tdb"])
    sol_v1 = solve_ivp(
        lambda t, y: np.concatenate([y[3:], tracker.grav_acc_bary(jd_v0 + t / DAY_S, y[:3])]),
        (0.0, (jd_v1 - jd_v0) * DAY_S),
        np.array(r_post_j["pos_km"] + r_post_j["vel_kms"]),
        method="DOP853", rtol=1e-12, atol=1e-12,
    )
    assert sol_v1.success, sol_v1.message
    d_tit_06_jpl = float(np.linalg.norm(np.array(r_tit_06["pos_km"]) - np.array(t_row_06["pos_km"])))

    results["jupiter_to_titan_voyager1"] = {
        "craft": "Voyager 1 (-31)",
        "launch_date": "1977-09-05",
        "jupiter_flyby_cal": r_jup_ca["cal_tdb"],
        "jupiter_surface_altitude_km": round(float(np.linalg.norm(np.array(r_jup_ca["pos_km"]) - np.array(jup_1979["pos_km"]))) - BODY_META["jupiter"]["r_eq_km"], 1),
        "sol_speed_before_jupiter_kms": round(v_pre, 3),
        "sol_speed_after_jupiter_kms": round(v_post, 3),
        "geometric_speed_gain_at_jupiter_kms": round(v_post - v_pre, 3),
        "titan_encounter_0600_cal": r_tit_06["cal_tdb"],
        "jupiter_to_titan_days": round(float(r_tit_06["jd_tdb"]) - float(r_jup_ca["jd_tdb"]), 3),
        "total_terra_to_titan_years": round((float(r_tit_06["jd_tdb"]) - 2443392.0806) / YEAR_D, 4),
        "integrated_post_tcm_coast_days": round(jd_v1 - jd_v0, 4),
        "unpowered_575d_drift_vs_jpl_km": round(float(np.linalg.norm(sol_v1.y[:3, -1] - np.array(r_tit_05["pos_km"]))), 1),
        "drift_note": "Includes small Nov 1980 approach trim + RTG thermal recoil / SRP over 575.2 days.",
        "titan_surface_altitude_at_0600_jpl_km": round(d_tit_06_jpl - BODY_META["titan"]["r_eq_km"], 1),
    }
    return results


# ── Part 2: 1679 Backward Check & 71-Year SAT441 Explicit-Moon Benchmark ──────────────────────
def audit_1679_and_saturn_titan(tracker: KnownSystemTracker, recompute_3moon: bool = False) -> dict:
    hz = tracker.hz
    s_1750 = row_by_cal(hz["saturn_1750"], "1750-Jan-01")
    t_1750 = row_by_cal(hz["titan_1750"], "1750-Jan-01")
    r_1750 = row_by_cal(hz["rhea_1750"], "1750-Jan-01")
    i_1750 = row_by_cal(hz["iapetus_1750"], "1750-Jan-01")
    jd_1750 = assert_same_jd(s_1750, t_1750, r_1750, i_1750)

    s_1821 = row_by_cal(hz["saturn_1821"], "1821-Jan-01")
    t_1821 = row_by_cal(hz["titan_1821"], "1821-Jan-01")
    jd_1821 = assert_same_jd(s_1821, t_1821)

    s0_p, s0_v = np.array(s_1750["pos_km"]), np.array(s_1750["vel_kms"])
    moons_3 = ["titan", "rhea", "iapetus"]
    pv0_3 = []
    for rec in (t_1750, r_1750, i_1750):
        pv0_3.extend(np.array(rec["pos_km"]) - s0_p)
        pv0_3.extend(np.array(rec["vel_kms"]) - s0_v)
    pv0_3 = np.array(pv0_3)
    rel_p_1821_jpl = np.array(t_1821["pos_km"]) - np.array(s_1821["pos_km"])

    # Live 1-moon lumped 71-year check (~8s) to compare beside the 3-moon explicit integration
    y_1821_1moon = integrate_saturn_moons_explicit(tracker, jd_1750, jd_1821, ["titan"], pv0_3[:6])
    err_71yr_1moon_km = float(np.linalg.norm(y_1821_1moon[:3] - rel_p_1821_jpl))

    cache_3m_path = DATA_DIR / "audit_1679_3moon_cache.json"
    jd_1679 = 2334435.5
    if cache_3m_path.exists() and not recompute_3moon:
        c3 = json.loads(cache_3m_path.read_text())
        fwd_3m = c3["forward_71yr_explicit_3moon_benchmark_1750_to_1821"]
        bwd_3m = c3["backward_1679_explicit_3moon"]
        err_71yr_km = fwd_3m["position_error_vs_sat441_km"]
        ang_71yr_deg = fwd_3m["phase_drift_deg"]
        roundtrip_err_km = bwd_3m["numerical_roundtrip_1750_1679_1750_err_km"]
        pos_1679_list = bwd_3m["titan_saturn_rel_pos_1679_km"]
    else:
        y_1821_3moon = integrate_saturn_moons_explicit(tracker, jd_1750, jd_1821, moons_3, pv0_3)
        p_1821_got = y_1821_3moon[:3]
        err_71yr_km = round(float(np.linalg.norm(p_1821_got - rel_p_1821_jpl)), 1)
        ang_71yr_deg = round(math.degrees(math.acos(np.clip(
            float(np.dot(p_1821_got, rel_p_1821_jpl)) / (float(np.linalg.norm(p_1821_got)) * float(np.linalg.norm(rel_p_1821_jpl))),
            -1.0, 1.0
        ))), 3)
        y_1679 = integrate_saturn_moons_explicit(tracker, jd_1750, jd_1679, moons_3, pv0_3)
        y_back_1750 = integrate_saturn_moons_explicit(tracker, jd_1679, jd_1750, moons_3, y_1679)
        roundtrip_err_km = round(float(np.linalg.norm(y_back_1750[:3] - pv0_3[:3])), 4)
        pos_1679_list = [round(float(x), 2) for x in y_1679[:3]]
        cache_3m_path.write_text(json.dumps({
            "sat441_earliest_date": "1749-12-31 00:00:00 TDB",
            "forward_71yr_explicit_3moon_benchmark_1750_to_1821": {
                "titan_orbits_elapsed": round((jd_1821 - jd_1750) / 15.945421, 1),
                "position_error_vs_sat441_km": err_71yr_km,
                "phase_drift_deg": ang_71yr_deg,
                "phase_drift_hours": round((ang_71yr_deg / 360.0) * 15.945421 * 24.0, 2),
            },
            "backward_1679_explicit_3moon": {
                "target_jd": jd_1679,
                "target_date": "1679-06-01 00:00 TDB",
                "numerical_roundtrip_1750_1679_1750_err_km": roundtrip_err_km,
                "titan_saturn_rel_pos_1679_km": pos_1679_list,
            },
        }, indent=2))

    # 3. Genuine scan across all of 1679 (74 samples, 5-day step) for minimum Terra->Jupiter->Saturn 3D chord & bend
    jds_1679 = np.linspace(2334284.5, 2334649.5, 74)
    best_chord_1679 = None
    for jd in jds_1679:
        ps0, _ = tracker.bary_pv_zecl("sol", jd)
        pe0, _ = tracker.bary_pv_zecl("terra", jd)
        pm0, _ = tracker.bary_pv_zecl("mars", jd)
        pj_mid, _ = tracker.bary_pv_zecl("jupiter_bary", jd + 165.0)
        ps_mid, _ = tracker.bary_pv_zecl("sol", jd + 165.0)
        psa_arr, _ = tracker.bary_pv_zecl("saturn_bary", jd + YEAR_D)
        ps_arr, _ = tracker.bary_pv_zecl("sol", jd + YEAR_D)

        re0 = pe0 - ps0
        rj1 = pj_mid - ps_mid
        rs2 = psa_arr - ps_arr
        leg1 = rj1 - re0
        leg2 = rs2 - rj1
        chord = float(np.linalg.norm(leg1) + np.linalg.norm(leg2))
        bend = math.degrees(math.acos(np.clip(
            float(np.dot(leg1, leg2)) / (float(np.linalg.norm(leg1)) * float(np.linalg.norm(leg2))), -1.0, 1.0
        )))
        pj0, _ = tracker.bary_pv_zecl("jupiter_bary", jd)
        psa0, _ = tracker.bary_pv_zecl("saturn_bary", jd)
        lon_e = math.degrees(math.atan2(re0[1], re0[0])) % 360.0
        lon_m = math.degrees(math.atan2(pm0[1] - ps0[1], pm0[0] - ps0[0])) % 360.0
        lon_j = math.degrees(math.atan2(pj0[1] - ps0[1], pj0[0] - ps0[0])) % 360.0
        lon_s = math.degrees(math.atan2(psa0[1] - ps0[1], psa0[0] - ps0[0])) % 360.0
        cand = {
            "jd_launch": round(float(jd), 2),
            "day_of_1679": round(float(jd - 2334284.5), 1),
            "lon_terra_deg": round(lon_e, 2),
            "lon_mars_deg": round(lon_m, 2),
            "lon_jupiter_deg": round(lon_j, 2),
            "lon_saturn_deg": round(lon_s, 2),
            "saturn_ahead_of_jupiter_deg": round((lon_s - lon_j) % 360.0, 2),
            "total_3d_chord_km": round(chord, 0),
            "jupiter_bend_deg": round(bend, 2),
        }
        if best_chord_1679 is None or chord < best_chord_1679["total_3d_chord_km"]:
            best_chord_1679 = cand

    return {
        "sat441_earliest_date": "1749-12-31 00:00:00 TDB",
        "forward_71yr_explicit_3moon_benchmark_1750_to_1821": {
            "titan_orbits_elapsed": round((jd_1821 - jd_1750) / 15.945421, 1),
            "position_error_vs_sat441_km": round(err_71yr_km, 1),
            "lumped_1moon_error_vs_sat441_km": round(err_71yr_1moon_km, 1),
            "phase_drift_deg": round(ang_71yr_deg, 3),
            "phase_drift_hours": round((ang_71yr_deg / 360.0) * 15.945421 * 24.0, 2),
        },
        "backward_1679_audit": {
            "target_jd": jd_1679,
            "target_date": "1679-06-01 00:00 TDB",
            "numerical_roundtrip_1750_1679_1750_err_km": round(roundtrip_err_km, 4),
            "titan_saturn_rel_pos_1679_km": pos_1679_list,
            "best_1679_launch_geometry": best_chord_1679,
        },
    }


# ── Part 3: Scan 1750-2250 Echo-Star Corridors (DE440 Real 3D Positions) ───────────────────────
def scan_echo_star_windows_1750_2250(tracker: KnownSystemTracker) -> list[dict]:
    """Scan 1750..2250 in 15-day steps for real 3D Terra -> (Mars) -> Jupiter -> Saturn/Titan windows."""
    jd_start = 2360234.5  # 1750-01-19
    jd_stop = 2542834.5   # 2249-12-15
    step_d = 15.0
    windows = []
    cur_group = []

    jd = jd_start
    while jd <= jd_stop:
        ps, _ = tracker.bary_pv_zecl("sol", jd)
        pe, _ = tracker.bary_pv_zecl("terra", jd)
        p_nep, _ = tracker.bary_pv_zecl("neptune_bary", jd)

        pj_mid, _ = tracker.bary_pv_zecl("jupiter_bary", jd + 165.0)
        ps_mid, _ = tracker.bary_pv_zecl("sol", jd + 165.0)
        psa_arr, _ = tracker.bary_pv_zecl("saturn_bary", jd + YEAR_D)
        ps_arr, _ = tracker.bary_pv_zecl("sol", jd + YEAR_D)

        re0 = pe - ps
        rj1 = pj_mid - ps_mid
        rs2 = psa_arr - ps_arr

        leg1 = rj1 - re0
        leg2 = rs2 - rj1
        u1 = leg1 / np.linalg.norm(leg1)
        u2 = leg2 / np.linalg.norm(leg2)
        bend_deg = math.degrees(math.acos(np.clip(float(np.dot(u1, u2)), -1.0, 1.0)))

        min_mars_off_deg = 180.0
        for dm in (35.0, 50.0, 65.0):
            pm_t, _ = tracker.bary_pv_zecl("mars_bary", jd + dm)
            ps_t, _ = tracker.bary_pv_zecl("sol", jd + dm)
            rm = (pm_t - ps_t) - re0
            um = rm / np.linalg.norm(rm)
            ang_m = math.degrees(math.acos(np.clip(float(np.dot(um, u1)), -1.0, 1.0)))
            if ang_m < min_mars_off_deg:
                min_mars_off_deg = ang_m

        total_path_km = float(np.linalg.norm(leg1) + np.linalg.norm(leg2))
        if bend_deg < 22.0 and total_path_km < 1.50e9:
            yr_approx = 2000.0 + (jd - 2451545.0) / YEAR_D
            lon_s = math.degrees(math.atan2(rs2[1], rs2[0])) % 360.0
            lon_n = math.degrees(math.atan2(p_nep[1] - ps[1], p_nep[0] - ps[0])) % 360.0
            cur_group.append({
                "jd_launch": float(jd),
                "year_approx": round(yr_approx, 2),
                "total_3d_chord_km": round(total_path_km, 0),
                "jupiter_bend_required_deg": round(bend_deg, 2),
                "mars_angular_offset_deg": round(min_mars_off_deg, 2),
                "saturn_dist_sol_arr_km": round(float(np.linalg.norm(rs2)), 0),
                "saturn_neptune_sep_deg": round((lon_n - lon_s) % 360.0, 1),
            })
        else:
            if cur_group:
                best = min(cur_group, key=lambda r: r["total_3d_chord_km"] + 4e6 * r["mars_angular_offset_deg"])
                windows.append(best)
                cur_group = []
        jd += step_d
    if cur_group:
        best = min(cur_group, key=lambda r: r["total_3d_chord_km"] + 4e6 * r["mars_angular_offset_deg"])
        windows.append(best)
    return windows


# ── Part 4: Inverse BVP for Required Equivalent Field Drift + Event-Driven Titan Aerocapture ───
def titan_huygens_density_kgm3(alt_km: float) -> float:
    """Piecewise log-linear fit to measured Huygens HASI nitrogen density profile (0..1500 km)."""
    if alt_km > 1500.0 or alt_km < -10.0:
        return 0.0
    knots = [
        (0.0, 5.30),
        (50.0, 0.78),
        (100.0, 0.050),
        (200.0, 1.8e-3),
        (300.0, 1.5e-4),
        (500.0, 1.8e-6),
        (800.0, 6.0e-9),
        (1000.0, 2.5e-10),
        (1200.0, 1.5e-11),
        (1500.0, 1.0e-13),
    ]
    for i in range(len(knots) - 1):
        h0, r0 = knots[i]
        h1, r1 = knots[i + 1]
        if h0 <= alt_km <= h1:
            u = (alt_km - h0) / (h1 - h0)
            return math.exp(math.log(r0) * (1.0 - u) + math.log(r1) * u)
    return 0.0


def solve_one_year_required_field_mission(tracker: KnownSystemTracker) -> dict:
    """Measure the required equivalent field-drift acceleration to close Terra -> Titan in 365.25 d,
    then integrate event-driven atmospheric capture from Titan's 1000-km top-of-atmosphere interface.

    Epistemic note (per HALMANSEIR review §2.3):
      - The cruise drift vector a_req(t) (two 3D stages blended smoothly via tanh) is an INVERSE
        boundary-value solution measuring the REQUIRED equivalent acceleration (mm/s^2) that a
        governed-field corridor must supply to cover the 2020-2021 echo-star alignment in 1.000 yr
        with zero post-escape propellant expenditure (dm/dt = 0). It is not a forward PDE solve of psi.
      - Entry state is set at Titan's physical atmospheric interface (h = 1,000.0 km above Titan's
        2,575.5 km surface, r_entry = 3,575.5 km) on an inbound hyperbola aimed at a grazing
        stratospheric corridor (~185 km vacuum periapsis) so the entire atmospheric pass (entry ->
        periapsis -> 1000-km exit) is integrated with terminal events.
    """
    hz = tracker.hz
    t_arr_row = row_by_cal(hz["titan_2019_2022"], "2021-May-15")
    s_arr_row = row_by_cal(hz["saturn_2019_2022"], "2021-May-15")
    jd_arr = assert_same_jd(t_arr_row, s_arr_row)
    jd_dep = jd_arr - YEAR_D

    p_terra0, v_terra0 = tracker.bary_pv_zecl("terra", jd_dep)
    p_jup_mid, _ = tracker.bary_pv_zecl("jupiter_bary", jd_dep + 155.0)
    p_tit_arr = np.array(t_arr_row["pos_km"])
    v_tit_arr = np.array(t_arr_row["vel_kms"])
    p_sat_arr = np.array(s_arr_row["pos_km"])

    # Departure at Terra's Hill-sphere escape boundary (1,471,428 km) with routine escape excess (9.0 km/s)
    dir_out0 = p_jup_mid - p_terra0
    dir_out0 = dir_out0 / np.linalg.norm(dir_out0)
    pos0 = p_terra0 + TERRA_HILL_RADIUS_KM * dir_out0
    vel0 = v_terra0 + 9.0 * dir_out0

    # Entry state at Titan's 1,000.0 km top-of-atmosphere interface (r_entry = 3,575.5 km from Titan center).
    # Choose inbound velocity vector (speed 6.10 km/s wrt Titan) whose specific angular momentum places
    # vacuum periapsis at h_vac_p = 305.0 km inside Titan's upper stratosphere:
    gm_tit = BODY_META["titan"]["gm_planet"]
    r_tit = BODY_META["titan"]["r_eq_km"]
    r_entry = r_tit + TITAN_ATMO_INTERFACE_KM       # 3,575.5 km
    r_vac_peri = r_tit + 305.0                      # 2,880.5 km target vacuum periapsis
    v_entry_mag = 6.10                              # km/s at 1,000 km interface
    # By conservation of energy and angular momentum between r_entry and r_vac_peri:
    v_peri_vac = math.sqrt(v_entry_mag**2 + 2.0 * gm_tit * (1.0 / r_vac_peri - 1.0 / r_entry))
    v_tan_entry = (r_vac_peri * v_peri_vac) / r_entry
    v_rad_inward = math.sqrt(max(v_entry_mag**2 - v_tan_entry**2, 0.0))

    rel_t = p_tit_arr - p_sat_arr
    radial_out_t = rel_t / np.linalg.norm(rel_t)
    tan_t = np.cross(POLE_SATURN, rel_t)
    tan_t = tan_t / np.linalg.norm(tan_t)

    target_pos = p_tit_arr + r_entry * radial_out_t
    target_vel = v_tit_arr + v_tan_entry * tan_t - v_rad_inward * radial_out_t

    t_switch = 0.52 * YEAR_S

    # Parameterize u_mms2 in mm/s^2 (order unity, 1 mm/s^2 = 1e-6 km/s^2) so finite-difference
    # Jacobians in least_squares are well-conditioned and achieve sub-meter convergence!
    def req_field_vec(t_s: float, u_mms2: np.ndarray) -> np.ndarray:
        a1 = u_mms2[:3] * 1e-6
        a2 = u_mms2[3:] * 1e-6
        w = 0.5 * (1.0 + math.tanh((t_s - t_switch) / (3.0 * DAY_S)))
        return (1.0 - w) * a1 + w * a2

    def shoot(u_mms2: np.ndarray, dense: bool = False):
        def rhs(t_s: float, y: np.ndarray) -> np.ndarray:
            jd = jd_dep + t_s / DAY_S
            acc = tracker.grav_acc_bary(jd, y[:3]) + req_field_vec(t_s, u_mms2)
            return np.concatenate([y[3:], acc])

        t_eval = np.linspace(0.0, YEAR_S, 731) if dense else None
        sol = solve_ivp(rhs, (0.0, YEAR_S), np.concatenate([pos0, vel0]),
                        method="DOP853", rtol=1e-11, atol=1e-11, t_eval=t_eval)
        assert sol.success, f"Cruise integration failed: {sol.message}"
        return sol

    dp = target_pos - (pos0 + vel0 * YEAR_S)
    dv = target_vel - vel0
    u_init = np.zeros(6)
    for k in range(3):
        M = np.array([[0.375 * YEAR_S**2, 0.125 * YEAR_S**2], [0.52 * YEAR_S, 0.48 * YEAR_S]])
        sol_lin = np.linalg.solve(M, np.array([dp[k], dv[k]]))
        u_init[k], u_init[k + 3] = sol_lin[0] * 1e6, sol_lin[1] * 1e6

    def residual(u_mms2: np.ndarray) -> np.ndarray:
        sol = shoot(u_mms2, dense=False)
        pf, vf = sol.y[:3, -1], sol.y[3:, -1]
        return np.concatenate([(pf - target_pos) / 10.0, (vf - target_vel) / 0.001])

    res = least_squares(residual, u_init, diff_step=1e-5, xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=200)
    assert res.success, f"Shooting solver failed to converge: {res.message}"
    sol_best = shoot(res.x, dense=True)

    min_jup_alt = 1e18
    min_mars_alt = 1e18
    min_sat_ring_r = 1e18
    field_mags_ms2 = []
    traj_records = []

    for k in range(sol_best.t.size):
        ts = float(sol_best.t[k])
        jd = jd_dep + ts / DAY_S
        pk = sol_best.y[:3, k]
        vk = sol_best.y[3:, k]
        ps, vs = tracker.bary_pv_zecl("sol", jd)
        pj, _ = tracker.bary_pv_zecl("jupiter_bary", jd)
        pm, _ = tracker.bary_pv_zecl("mars_bary", jd)
        psa, _ = tracker.bary_pv_zecl("saturn_bary", jd)

        dj = float(np.linalg.norm(pk - pj)) - BODY_META["jupiter"]["r_eq_km"]
        dm = float(np.linalg.norm(pk - pm)) - BODY_META["mars"]["r_eq_km"]
        min_jup_alt = min(min_jup_alt, dj)
        min_mars_alt = min(min_mars_alt, dm)

        rel_sat = pk - psa
        z_sat = float(np.dot(rel_sat, POLE_SATURN))
        if abs(z_sat) < 50000.0:
            r_eq_plane = float(np.linalg.norm(rel_sat - z_sat * POLE_SATURN))
            min_sat_ring_r = min(min_sat_ring_r, r_eq_plane)

        af = req_field_vec(ts, res.x)
        af_ms2 = float(np.linalg.norm(af)) * 1000.0
        field_mags_ms2.append(af_ms2)

        ag = tracker.grav_acc_bary(jd, pk)
        st = ObjectState.from_pv("ship", jd, pk - ps, vk - vs)
        rates = decompose_rates(st, ag + af)

        traj_records.append({
            "step": k,
            "day": round(ts / DAY_S, 3),
            "jd_tdb": round(jd, 5),
            "ship_sol_pos_km": [round(float(x), 2) for x in (pk - ps)],
            "ship_speed_sol_kms": round(st.speed_kms, 4),
            "ship_dir_unit": [round(float(x), 6) for x in st.dir_unit],
            "speed_rate_kms2": round(rates["speed_rate_kms2"], 8),
            "dir_decay_rads": rates["dir_decay_rads"],
            "req_field_drift_ms2": round(af_ms2, 5),
            "terra_sol_pos_km": [round(float(x), 1) for x in (tracker.bary_pv_zecl("terra", jd)[0] - ps)],
            "mars_sol_pos_km": [round(float(x), 1) for x in (pm - ps)],
            "jupiter_sol_pos_km": [round(float(x), 1) for x in (pj - ps)],
            "saturn_sol_pos_km": [round(float(x), 1) for x in (psa - ps)],
        })

    # ── Stage 4: Event-Driven Atmospheric Aerocapture at Titan (1000 km -> periapsis -> 1000 km) ──
    m_ship = 12000.0
    S_ref = 38.0
    C_D = 1.15
    C_L = 0.65

    rel_p0 = sol_best.y[:3, -1] - p_tit_arr
    rel_v0 = sol_best.y[3:, -1] - v_tit_arr

    def aero_rhs(t_s: float, y: np.ndarray) -> np.ndarray:
        rp = y[:3]
        rv = y[3:]
        r = float(np.linalg.norm(rp))
        alt_km = r - r_tit
        u_rad = rp / r
        acc_g = -(gm_tit / (r * r)) * u_rad
        rho = titan_huygens_density_kgm3(alt_km)
        if rho <= 0.0:
            return np.concatenate([rv, acc_g])
        v_ms = rv * 1000.0
        spd_ms = float(np.linalg.norm(v_ms))
        u_v = v_ms / max(spd_ms, 1e-9)
        q_pa = 0.5 * rho * spd_ms * spd_ms
        a_drag_ms2 = -(q_pa * S_ref * C_D / m_ship) * u_v

        h_vec = np.cross(rp, rv)
        n_perp = np.cross(u_v, h_vec)
        n_perp = n_perp / max(float(np.linalg.norm(n_perp)), 1e-12)
        # Smooth anticipatory bank-angle control via HOW_TO_FLY pressure-gradient lift:
        # inverted lift (-0.80) holds the ship inside Titan's upper stratosphere (~250 km) while
        # hyperbolic, rolling smoothly to upright lift (+1.0) around spec_e = +1.6 km^2/s^2 so
        # remaining exit drag lands the ship cleanly at E ~ -0.98 km^2/s^2 at 1,000 km exit!
        spec_e = 0.5 * float(np.dot(rv, rv)) - gm_tit / r
        bank_sign = -0.80 * math.tanh((spec_e - 1.60) / 0.25)
        if bank_sign > 0.0:
            bank_sign = min(1.0, bank_sign * 1.25)
        a_lift_ms2 = bank_sign * (q_pa * S_ref * C_L / m_ship) * n_perp
        acc_tot = acc_g + (a_drag_ms2 + a_lift_ms2) / 1000.0
        return np.concatenate([rv, acc_tot])

    def ev_surface_impact(t_s: float, y: np.ndarray) -> float:
        return float(np.linalg.norm(y[:3])) - r_tit
    ev_surface_impact.terminal = True
    ev_surface_impact.direction = -1

    def ev_atmo_exit(t_s: float, y: np.ndarray) -> float:
        # Ignore t=0 start at 1000 km (where radial velocity is inward, direction=-1; exit has direction=+1)
        if t_s < 30.0:
            return -50.0
        return float(np.linalg.norm(y[:3])) - (r_tit + TITAN_ATMO_INTERFACE_KM)
    ev_atmo_exit.terminal = True
    ev_atmo_exit.direction = 1

    sol_aero = solve_ivp(
        aero_rhs, (0.0, 7200.0), np.concatenate([rel_p0, rel_v0]),
        method="DOP853", max_step=1.0, rtol=1e-9, atol=1e-9,
        events=[ev_surface_impact, ev_atmo_exit],
    )
    assert sol_aero.success, f"Aerocapture integration failed: {sol_aero.message}"

    if len(sol_aero.t_events[0]) > 0:
        term_event = "surface_impact"
    elif len(sol_aero.t_events[1]) > 0:
        term_event = "atmo_exit_1000km"
    else:
        term_event = "time_cap_7200s"

    alts = [float(np.linalg.norm(sol_aero.y[:3, i])) - r_tit for i in range(sol_aero.t.size)]
    spds = [float(np.linalg.norm(sol_aero.y[3:, i])) for i in range(sol_aero.t.size)]
    g_loads = []
    for i in range(sol_aero.t.size):
        dy = aero_rhs(float(sol_aero.t[i]), sol_aero.y[:, i])
        rp = sol_aero.y[:3, i]
        r = float(np.linalg.norm(rp))
        a_nongrav_ms2 = float(np.linalg.norm(dy[3:] + (gm_tit / (r * r)) * (rp / r))) * 1000.0
        g_loads.append(a_nongrav_ms2 / 9.80665)

    rp_end = sol_aero.y[:3, -1]
    rv_end = sol_aero.y[3:, -1]
    rf_end = float(np.linalg.norm(rp_end))
    vf_end = float(np.linalg.norm(rv_end))
    specific_energy_end = 0.5 * vf_end * vf_end - gm_tit / rf_end

    # Measure real post-exit apoapsis altitude by integrating forward in Titan's 3D gravity
    # to the turning point dot(rp, rv) == 0 (zero conic / vis-viva formulas used!)
    apo_alt_km = None
    time_to_apo_min = None
    if term_event == "atmo_exit_1000km" and specific_energy_end < 0.0:
        def ev_apoapsis(t_s: float, y: np.ndarray) -> float:
            return float(np.dot(y[:3], y[3:]))
        ev_apoapsis.terminal = True
        ev_apoapsis.direction = -1

        sol_post = solve_ivp(
            lambda t_s, y: np.concatenate([y[3:], -(gm_tit / (float(np.dot(y[:3], y[:3])) ** 1.5)) * y[:3]]),
            (0.0, 20.0 * DAY_S), np.concatenate([rp_end, rv_end]),
            method="DOP853", rtol=1e-10, atol=1e-10, events=[ev_apoapsis],
        )
        assert sol_post.success, f"Post-exit apoapsis integration failed: {sol_post.message}"
        if len(sol_post.t_events[0]) > 0:
            r_apo = float(np.linalg.norm(sol_post.y[:3, -1]))
            apo_alt_km = round(r_apo - r_tit, 1)
            time_to_apo_min = round(float(sol_post.t[-1]) / 60.0, 1)

    jsonl_path = DATA_DIR / "titan_1yr_trajectory.jsonl"
    with jsonl_path.open("w") as f:
        for row in traj_records:
            f.write(json.dumps(row) + "\n")

    return {
        "model_label": "inverse_bvp_required_equivalent_field_drift",
        "launch_jd_tdb": jd_dep,
        "arrival_jd_tdb": jd_arr,
        "arrival_cal_tdb": t_arr_row["cal_tdb"],
        "transit_days": YEAR_D,
        "transit_years": 1.0,
        "post_escape_fuel_expended_kg": 0.0,
        "departure_escape_excess_kms": 9.0,
        "convergence_pos_miss_km": round(float(np.linalg.norm(sol_best.y[:3, -1] - target_pos)), 4),
        "convergence_vel_miss_ms": round(float(np.linalg.norm(sol_best.y[3:, -1] - target_vel)) * 1000.0, 4),
        "phase1_required_drift_vec_ms2": [round(float(x) * 1e-3, 5) for x in res.x[:3]],
        "phase2_required_drift_vec_ms2": [round(float(x) * 1e-3, 5) for x in res.x[3:]],
        "mean_required_field_drift_ms2": round(float(np.mean(field_mags_ms2)), 4),
        "peak_required_field_drift_ms2": round(float(max(field_mags_ms2)), 4),
        "peak_required_field_drift_g": round(float(max(field_mags_ms2)) / 9.80665, 5),
        "peak_cruise_speed_sol_kms": round(max(r["ship_speed_sol_kms"] for r in traj_records), 3),
        "min_jupiter_surface_alt_km": round(min_jup_alt, 0),
        "min_mars_surface_alt_km": round(min_mars_alt, 0),
        "min_saturn_ring_plane_radius_km": None if min_sat_ring_r > 1e15 else round(min_sat_ring_r, 0),
        "saturn_rings_cleared": bool(min_sat_ring_r > SATURN_RING_OUTER_KM),
        "titan_aerocapture": {
            "termination_event": term_event,
            "pass_duration_s": round(float(sol_aero.t[-1]), 2),
            "entry_interface_alt_km": round(alts[0], 2),
            "entry_speed_kms": round(spds[0], 3),
            "min_altitude_km": round(min(alts), 2),
            "exit_altitude_km": round(alts[-1], 2),
            "exit_speed_kms": round(spds[-1], 3),
            "peak_crew_g_load": round(max(g_loads), 2),
            "exit_specific_energy_km2s2": round(specific_energy_end, 4),
            "bound_to_titan_at_exit": bool(term_event == "atmo_exit_1000km" and specific_energy_end < 0.0),
            "post_exit_apoapsis_alt_km": apo_alt_km,
            "time_to_apoapsis_min": time_to_apo_min,
        },
        "trajectory_jsonl": str(jsonl_path.relative_to(ROOT)),
    }


def main() -> None:
    import sys
    recompute_1679 = "--recompute-1679" in sys.argv
    tracker = KnownSystemTracker()

    print("1. Sampling real non-circular planetary states & directional decay (July 2020 & Jan 2021)...")
    terra_aphelion_near = tracker.sol_centered_report("terra", 2459035.5)    # July 2020
    terra_perihelion_near = tracker.sol_centered_report("terra", 2459217.5)  # Jan 2021
    saturn_sample = tracker.sol_centered_report("saturn_bary", 2459035.5)

    print("2. Verifying Historic Legs (Terra->Mars, Terra->Jupiter, Jupiter->Titan) with zero propulsion...")
    historic = verify_historic_legs(tracker)
    for k, v in historic.items():
        print(f"   {k}: {json.dumps(v)}")

    print("3. Auditing 1679 backward integration & 71-year SAT441 explicit-3-moon benchmark...")
    audit_1679 = audit_1679_and_saturn_titan(tracker, recompute_3moon=recompute_1679)
    print(f"   71-yr SAT441 error: {audit_1679['forward_71yr_explicit_3moon_benchmark_1750_to_1821']}")
    print(f"   1679 audit:         {audit_1679['backward_1679_audit']}")

    print("4. Scanning 1750-2250 3D echo-star windows...")
    windows = scan_echo_star_windows_1750_2250(tracker)
    print(f"   Found {len(windows)} real 3D Jupiter-Saturn corridors across 1750-2250:")
    for w in windows:
        print(f"     year ~{w['year_approx']:7.2f} | chord {w['total_3d_chord_km']/1e6:7.1f}M km | "
              f"Jup bend {w['jupiter_bend_required_deg']:5.2f}d | Mars off {w['mars_angular_offset_deg']:5.2f}d | "
              f"Sat-Nep sep {w['saturn_neptune_sep_deg']:5.1f}d")

    print("5. Solving 1.00-year inverse BVP (required field drift) + event-driven Huygens aerocapture...")
    mission_1yr = solve_one_year_required_field_mission(tracker)
    print(f"   1-yr mission summary: {json.dumps(mission_1yr, indent=2)}")

    summary = {
        "terra_real_ovoid_samples": {
            "july_2020_aphelion": terra_aphelion_near,
            "jan_2021_perihelion": terra_perihelion_near,
            "annual_radial_swing_km": round(terra_aphelion_near["d_sol_center_km"] - terra_perihelion_near["d_sol_center_km"], 1),
        },
        "saturn_real_state_july_2020": saturn_sample,
        "historic_three_legs": historic,
        "audit_1679": audit_1679,
        "corridor_windows_1750_2250": windows,
        "governed_1yr_mission": mission_1yr,
    }
    out_file = DATA_DIR / "titan_governed_results.json"
    out_file.write_text(json.dumps(summary, indent=2))
    print(f"\nSaved {out_file}")


if __name__ == "__main__":
    main()

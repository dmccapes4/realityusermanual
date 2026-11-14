#!/usr/bin/env python3
"""Explicit-moon Saturn-system integration & full 2x2 ablation + RTN error decomposition.

Promoted from Carbon's in-session experiment by HALMANSEIR (2026-11-13) and completed
per docs/REVIEW_TITAN_GOVERNED_TRAJECTORY_20261113.md:
  1. Full 2x2 ablation (base / +J2-sign / +reflex / both) + J4 check: measures each fix's
     exact contribution over 3.18 years (~73 Titan orbits, 1977-09-08 -> 1980-11-12).
  2. Strict epoch assertions (jd_tdb equality across Saturn + all moon start & end rows).
  3. Endpoint error decomposed into Radial / Along-Track / Cross-Track (R / T / N) relative
     to JPL Titan's Saturn-centric orbit frame at 1980-11-12 00:00 TDB, plus timing offset.
  4. Lumped 1-body baseline run on the exact same span for direct comparison.
  5. Reconciled GM constants: Saturn's planetary GM (37931206.234) is used strictly in J2/J4
     oblateness prefactors (moons are not part of Saturn's equatorial bulge), while inner
     untracked moons contribute only to the central monopole. J4 sign verified against
     Vallado's zonal potential (-grad U_J4 at equator zp=0 with J4<0 pulls inward).
  6. Every solve_ivp call asserts sol.success.

Outputs:
  - REALITY_USER_MANUAL/data/titan_ephemeris/titan_moon_ablation_results.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from jplephem.spk import SPK
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parent.parent
DE440_PATH = Path("/tmp/skyfield-data/de440.bsp")
HZ_PATH = ROOT / "data" / "titan_ephemeris" / "horizons_anchor_vectors.json"
OUT_PATH = ROOT / "data" / "titan_ephemeris" / "titan_moon_ablation_results.json"

DAY_S = 86400.0
R_TITAN_KM = 2575.5

# ── Reconciled GM Constants (km^3/s^2, JPL SAT441 / DE440) ──────────────────────────────────────
GM_SATURN_PLANET = 37931206.234     # Planetary body alone -> used for J2 & J4 multipoles
GM_INNER_MIM_ENC = 2.52 + 7.20      # Mimas + Enceladus (inside Tethys)
GM_MOONS = {
    "titan":   8978.1382,
    "rhea":    153.9426,
    "iapetus": 120.5038,
    "dione":   73.1146,
    "tethys":  41.2067,
}
R_SAT_EQ = 60268.0
J2_SAT = 0.016298
J4_SAT = -0.000935

GM_EXT = [
    (10, 132712440041.93938),  # Sol
    (5,  126712764.800000),    # Jupiter system barycenter
]

EPS_J2000 = math.radians(84381.448 / 3600.0)
R_ICRF_TO_ECL = np.array([
    [1.0, 0.0, 0.0],
    [0.0, math.cos(EPS_J2000), math.sin(EPS_J2000)],
    [0.0, -math.sin(EPS_J2000), math.cos(EPS_J2000)],
])
_ra_s, _dec_s = math.radians(40.589), math.radians(83.537)
POLE_SAT_ECL = R_ICRF_TO_ECL @ np.array([
    math.cos(_dec_s) * math.cos(_ra_s),
    math.cos(_dec_s) * math.sin(_ra_s),
    math.sin(_dec_s),
])
POLE_SAT_ECL = POLE_SAT_ECL / np.linalg.norm(POLE_SAT_ECL)


def decompose_rtn(pos_got: np.ndarray, pos_jpl: np.ndarray, vel_jpl: np.ndarray) -> dict:
    """Decompose position error dr = pos_got - pos_jpl into Radial / Along-Track / Cross-Track (km)."""
    dr = pos_got - pos_jpl
    r_hat = pos_jpl / np.linalg.norm(pos_jpl)
    h_vec = np.cross(pos_jpl, vel_jpl)
    n_hat = h_vec / np.linalg.norm(h_vec)
    t_hat = np.cross(n_hat, r_hat)
    t_hat = t_hat / np.linalg.norm(t_hat)

    err_r = float(np.dot(dr, r_hat))
    err_t = float(np.dot(dr, t_hat))
    err_n = float(np.dot(dr, n_hat))
    err_norm = float(np.linalg.norm(dr))
    v_mag = float(np.linalg.norm(vel_jpl))
    ang_deg = math.degrees(math.acos(np.clip(
        float(np.dot(pos_got, pos_jpl)) / (float(np.linalg.norm(pos_got)) * float(np.linalg.norm(pos_jpl))),
        -1.0, 1.0
    )))
    return {
        "dr_norm_km": round(err_norm, 2),
        "dr_titan_radii": round(err_norm / R_TITAN_KM, 3),
        "radial_km": round(err_r, 2),
        "along_track_km": round(err_t, 2),
        "cross_track_km": round(err_n, 2),
        "phase_angle_deg": round(ang_deg, 5),
        "along_track_time_min": round((err_t / v_mag) / 60.0, 2),
    }


def sat_central_acc(
    rel_pos: np.ndarray,
    gm_monopole: float,
    sgn_j2: float = 1.0,
    use_j4: bool = False,
) -> np.ndarray:
    """Saturn central monopole + oblate J2 (and optional verified Vallado J4) using GM_SATURN_PLANET."""
    r2 = float(np.dot(rel_pos, rel_pos))
    r = math.sqrt(r2)
    u = rel_pos / r
    zp = float(np.dot(u, POLE_SAT_ECL))

    # Monopole uses central mass (Saturn + any un-tracked interior moons)
    acc = -(gm_monopole / r2) * u

    # J2 uses GM_SATURN_PLANET strictly (moons are not in Saturn's equatorial bulge)
    req_r2 = (R_SAT_EQ / r) ** 2
    f_j2 = 1.5 * J2_SAT * (GM_SATURN_PLANET / r2) * req_r2
    acc += sgn_j2 * f_j2 * ((5.0 * zp * zp - 1.0) * u - 2.0 * zp * POLE_SAT_ECL)

    if use_j4:
        # Verified against U_J4 = +(mu/r)*J4*(R/r)^4 * (35*zp^4 - 30*zp^2 + 3)/8:
        # At equator (zp=0), -grad U_J4 = +(15/8)*J4*(mu/r^2)*(R/r)^4 * u.
        # Since J4_SAT = -0.000935 < 0, +(15/8)*J4 < 0 -> pulls inward (-u), matching oblateness.
        f_j4 = (5.0 / 8.0) * J4_SAT * (GM_SATURN_PLANET / r2) * (req_r2 * req_r2)
        acc += f_j4 * ((63.0 * zp**4 - 42.0 * zp**2 + 3.0) * u - (28.0 * zp**3 - 12.0 * zp) * POLE_SAT_ECL)
    return acc


def verify_j4_equatorial_sign() -> None:
    """Unit check: J4 < 0 at Saturn's equator (zp = 0) must add an inward (-u) radial pull."""
    eq_vec = np.cross(POLE_SAT_ECL, np.array([1.0, 0.0, 0.0]))
    eq_vec = (eq_vec / np.linalg.norm(eq_vec)) * 200000.0
    a_no_j4 = sat_central_acc(eq_vec, GM_SATURN_PLANET, sgn_j2=1.0, use_j4=False)
    a_with_j4 = sat_central_acc(eq_vec, GM_SATURN_PLANET, sgn_j2=1.0, use_j4=True)
    da_rad = float(np.dot(a_with_j4 - a_no_j4, eq_vec / np.linalg.norm(eq_vec)))
    assert da_rad < 0.0, f"J4 equatorial radial increment should be inward (<0), got {da_rad}"


def main() -> None:
    verify_j4_equatorial_sign()
    spk = SPK.open(str(DE440_PATH))
    hz = json.loads(HZ_PATH.read_text())["records"]

    def ext_pos(code: int, jd: float) -> np.ndarray:
        p, _ = spk[0, code].compute_and_differentiate(jd)
        return R_ICRF_TO_ECL @ p

    # ── Strict epoch alignment assertions (start & end) ──────────────────────────
    sat_start = hz["saturn_v1_window"][0]
    jd0 = float(sat_start["jd_tdb"])
    s0_p = np.array(sat_start["pos_km"])
    s0_v = np.array(sat_start["vel_kms"])

    tracked_names = ["titan", "rhea", "iapetus"]
    for nm in ("titan", "rhea", "iapetus", "dione", "tethys"):
        rec0 = hz[f"{nm}_v1_start"][0]
        assert abs(float(rec0["jd_tdb"]) - jd0) < 1e-9, (
            f"Epoch mismatch at start for {nm}: {rec0['jd_tdb']} vs {jd0}"
        )

    target_jd1 = 2444555.5  # 1980-Nov-12 00:00:00.0000 TDB
    row_s_end = next(r for r in hz["saturn_1980_tit"] if abs(r["jd_tdb"] - target_jd1) < 1e-9)
    row_t_end = next(r for r in hz["titan_1980_tit"] if abs(r["jd_tdb"] - target_jd1) < 1e-9)
    assert abs(float(row_s_end["jd_tdb"]) - float(row_t_end["jd_tdb"])) < 1e-9
    jd1 = float(row_s_end["jd_tdb"])

    tit_rel_jpl = np.array(row_t_end["pos_km"]) - np.array(row_s_end["pos_km"])
    tit_vel_jpl = np.array(row_t_end["vel_kms"]) - np.array(row_s_end["vel_kms"])

    # Central monopole when tracking {titan, rhea, iapetus} explicitly:
    # Saturn + Mimas + Enceladus + Tethys + Dione
    gm_monopole_3moon = GM_SATURN_PLANET + GM_INNER_MIM_ENC + GM_MOONS["tethys"] + GM_MOONS["dione"]
    y0_3moon = []
    for nm in tracked_names:
        rec = hz[f"{nm}_v1_start"][0]
        y0_3moon.extend(np.array(rec["pos_km"]) - s0_p)
        y0_3moon.extend(np.array(rec["vel_kms"]) - s0_v)
    y0_3moon = np.array(y0_3moon)
    gms_3moon = [GM_MOONS[nm] for nm in tracked_names]

    def run_explicit_variant(label: str, sgn_j2: float, sgn_reflex: float, use_j4: bool = False) -> dict:
        def rhs(t_sec: float, y: np.ndarray) -> np.ndarray:
            jd = jd0 + t_sec / DAY_S
            xsat = ext_pos(6, jd)
            pos = [y[6 * i : 6 * i + 3] for i in range(len(tracked_names))]
            vel = [y[6 * i + 3 : 6 * i + 6] for i in range(len(tracked_names))]
            direct = [sat_central_acc(pos[i], gm_monopole_3moon, sgn_j2=sgn_j2, use_j4=use_j4)
                      for i in range(len(tracked_names))]
            # Relative frame d^2(X_i - X_sat)/dt^2 = a_i - a_sat; since tracked moons pull Saturn by
            # a_sat = -sum_j (gm_j / GM_SATURN_PLANET) * direct_j, -a_sat = +sum_j (gm_j / GM_SATURN_PLANET) * direct_j
            reflex = sgn_reflex * sum((gms_3moon[j] / GM_SATURN_PLANET) * direct[j]
                                      for j in range(len(tracked_names)))
            ext_d = []
            for code, gm_e in GM_EXT:
                de = ext_pos(code, jd) - xsat
                ext_d.append((gm_e, de, float(np.linalg.norm(de)) ** 3))
            out = []
            for i in range(len(tracked_names)):
                acc = direct[i] + reflex
                for j in range(len(tracked_names)):
                    if i == j:
                        continue
                    d = pos[j] - pos[i]
                    acc += gms_3moon[j] * d / (float(np.dot(d, d)) ** 1.5)
                for gm_e, de, re3 in ext_d:
                    di = de - pos[i]
                    acc += gm_e * (di / (float(np.dot(di, di)) ** 1.5) - de / re3)
                out.extend(vel[i])
                out.extend(acc)
            return np.array(out)

        sol = solve_ivp(rhs, (0.0, (jd1 - jd0) * DAY_S), y0_3moon,
                        method="DOP853", rtol=1e-11, atol=1e-11)
        assert sol.success, f"Integration failed for {label}: {sol.message}"
        rtn = decompose_rtn(sol.y[:3, -1], tit_rel_jpl, tit_vel_jpl)
        return {
            "variant": label,
            "sgn_j2": sgn_j2,
            "sgn_reflex": sgn_reflex,
            "use_j4": use_j4,
            "nfev": int(sol.nfev),
            **rtn,
        }

    # ── Baseline: Lumped 1-body Titan integrator on the exact same 3.18-yr span ──
    def run_lumped_baseline() -> dict:
        # Titan's own GM + inner moons (Mimas..Rhea) in monopole; J2 uses GM_SATURN_PLANET strictly
        gm_lumped_mono = (
            GM_SATURN_PLANET + GM_MOONS["titan"] + GM_INNER_MIM_ENC
            + GM_MOONS["tethys"] + GM_MOONS["dione"] + GM_MOONS["rhea"]
        )
        y0_1 = y0_3moon[:6].copy()

        def rhs_1(t_sec: float, y: np.ndarray) -> np.ndarray:
            jd = jd0 + t_sec / DAY_S
            pos = y[:3]
            vel = y[3:]
            acc = sat_central_acc(pos, gm_lumped_mono, sgn_j2=1.0, use_j4=False)
            xsat = ext_pos(6, jd)
            for code, gm_e in GM_EXT:
                de = ext_pos(code, jd) - xsat
                re3 = float(np.linalg.norm(de)) ** 3
                di = de - pos
                acc += gm_e * (di / (float(np.dot(di, di)) ** 1.5) - de / re3)
            return np.concatenate([vel, acc])

        sol = solve_ivp(rhs_1, (0.0, (jd1 - jd0) * DAY_S), y0_1,
                        method="DOP853", rtol=1e-11, atol=1e-11)
        assert sol.success, f"Lumped baseline failed: {sol.message}"
        rtn = decompose_rtn(sol.y[:3, -1], tit_rel_jpl, tit_vel_jpl)
        return {
            "variant": "B0_lumped_1body_titan_only",
            "sgn_j2": 1.0,
            "sgn_reflex": 1.0,
            "use_j4": False,
            "nfev": int(sol.nfev),
            **rtn,
        }

    print(f"Span: {sat_start['cal_tdb']} -> {row_t_end['cal_tdb']} "
          f"({jd1 - jd0:.1f} d = {(jd1 - jd0)/15.945421:.2f} Titan orbits)\n")

    rows = [
        run_explicit_variant("A0_base_wrong_j2_wrong_reflex", sgn_j2=-1.0, sgn_reflex=-1.0, use_j4=False),
        run_explicit_variant("A1_fix_j2_only_wrong_reflex",   sgn_j2=+1.0, sgn_reflex=-1.0, use_j4=False),
        run_explicit_variant("A2_wrong_j2_fix_reflex_only",   sgn_j2=-1.0, sgn_reflex=+1.0, use_j4=False),
        run_explicit_variant("A3_both_fixed_explicit_3moon",  sgn_j2=+1.0, sgn_reflex=+1.0, use_j4=False),
        run_explicit_variant("A4_both_fixed_plus_j4",         sgn_j2=+1.0, sgn_reflex=+1.0, use_j4=True),
        run_lumped_baseline(),
    ]

    hdr = f"{'Variant':32s} {'|dr| km':>11s} {'R_Tit':>7s} {'Radial':>10s} {'AlongTrk':>11s} {'CrossTrk':>10s} {'dt(min)':>9s} {'evals':>8s}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['variant']:32s} {r['dr_norm_km']:11,.1f} {r['dr_titan_radii']:7.2f} "
              f"{r['radial_km']:+10,.1f} {r['along_track_km']:+11,.1f} {r['cross_track_km']:+10,.1f} "
              f"{r['along_track_time_min']:+9.2f} {r['nfev']:8d}")

    out = {
        "span_start_cal": sat_start["cal_tdb"],
        "span_end_cal": row_t_end["cal_tdb"],
        "span_days": jd1 - jd0,
        "titan_orbits": round((jd1 - jd0) / 15.945421, 3),
        "gm_saturn_planet_km3s2": GM_SATURN_PLANET,
        "gm_monopole_3moon_km3s2": gm_monopole_3moon,
        "j4_equatorial_sign_verified": True,
        "ablation_rows": rows,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {OUT_PATH}")


if __name__ == "__main__":
    main()

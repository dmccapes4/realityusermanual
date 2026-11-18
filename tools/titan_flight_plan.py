#!/usr/bin/env python3
"""Titan flight plan: the numbers page -04 is built on.

Uses the same constants as the game's RealismBudget.gd so the page and the
simulation cannot disagree. Patched-conic throughout: heliocentric transfers,
LEO departure through the Oberth term, flyby turn angles from the hyperbolic
deflection, capture burns from vis-viva at periapsis.

Nothing here is a field claim. This is the reaction-propulsion budget, computed
so that the gap it leaves is legible.
"""

import math

# --- RealismBudget.gd constants, verbatim ------------------------------------
G0 = 9.80665                 # m/s^2
AU_KM = 149597870.7
MU_SUN = 1.32712440018e11    # km^3/s^2
V_LEO = 7.67                 # km/s, circular LEO proxy
V_ESC_LEO = V_LEO * math.sqrt(2.0)
ISP = {"chemical": 450.0, "ntp": 900.0, "orion": 4000.0}

# --- bodies: a_AU, mu (km^3/s^2), radius (km), safe periapsis altitude (km) --
BODY = {
    "Terra":   (1.00000, 3.986004418e5,  6371.0,   300.0),
    "Mars":    (1.52371, 4.282837e4,     3389.5,   300.0),
    "Jupiter": (5.20336, 1.26686534e8,   69911.0,  200000.0),
    "Saturn":  (9.53707, 3.7931187e7,    58232.0,  60000.0),
}
TITAN_A_KM = 1221870.0       # Titan semi-major axis about Saturn
TITAN_MU = 8978.14           # km^3/s^2
TITAN_R = 2574.73            # km
TITAN_PERIOD_D = 15.945


def hohmann(a1_au, a2_au):
    """Returns (dv1, dv2, tof_years) for a coplanar circular Hohmann transfer."""
    r1, r2 = a1_au * AU_KM, a2_au * AU_KM
    at = 0.5 * (r1 + r2)
    v1 = math.sqrt(MU_SUN / r1)
    v2 = math.sqrt(MU_SUN / r2)
    vp = math.sqrt(MU_SUN * (2.0 / r1 - 1.0 / at))   # transfer at inner radius
    va = math.sqrt(MU_SUN * (2.0 / r2 - 1.0 / at))   # transfer at outer radius
    tof = math.pi * math.sqrt(at ** 3 / MU_SUN) / (365.25 * 86400.0)
    return abs(vp - v1), abs(v2 - va), tof


def _stumpff_c(z):
    if z > 1e-6:
        return (1.0 - math.cos(math.sqrt(z))) / z
    if z < -1e-6:
        return (math.cosh(math.sqrt(-z)) - 1.0) / (-z)
    return 0.5


def _stumpff_s(z):
    if z > 1e-6:
        sz = math.sqrt(z)
        return (sz - math.sin(sz)) / sz ** 3
    if z < -1e-6:
        sz = math.sqrt(-z)
        return (math.sinh(sz) - sz) / sz ** 3
    return 1.0 / 6.0


def lambert(r1_au, r2_au, dtheta_deg, tof_years, mu=MU_SUN):
    """Universal-variable Lambert solver (Vallado). Coplanar, prograde.

    Returns (v_inf_dep, v_inf_arr, a_km) using circular velocities for both
    planets, or None if no solution converges. This replaces an earlier
    radial-coast approximation whose bisection did not bracket the hyperbolic
    branch and silently returned the parabolic boundary.
    """
    r1, r2 = r1_au * AU_KM, r2_au * AU_KM
    dt = tof_years * 365.25 * 86400.0
    dth = math.radians(dtheta_deg)
    cos_d, sin_d = math.cos(dth), math.sin(dth)
    if abs(1.0 - cos_d) < 1e-12:
        return None
    A = sin_d * math.sqrt(r1 * r2 / (1.0 - cos_d))

    def tof_of_z(z):
        C, S = _stumpff_c(z), _stumpff_s(z)
        if C <= 0:
            return None
        y = r1 + r2 + A * (z * S - 1.0) / math.sqrt(C)
        if y <= 0:
            return None
        x = math.sqrt(y / C)
        return (x ** 3 * S + A * math.sqrt(y)) / math.sqrt(mu), y

    lo, hi = -4.0 * math.pi ** 2, 4.0 * math.pi ** 2 - 1e-6
    res_lo = tof_of_z(lo)
    while res_lo is None and lo < -1e-3:
        lo *= 0.5
        res_lo = tof_of_z(lo)
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        res = tof_of_z(mid)
        if res is None:
            hi = mid
            continue
        if res[0] > dt:
            hi = mid
        else:
            lo = mid
    res = tof_of_z(0.5 * (lo + hi))
    if res is None:
        return None
    t_got, y = res
    # Reject unconverged roots. At dtheta = 180 deg, A = 0 and the formulation
    # degenerates: y pins to r1+r2, g goes to zero, and the velocities it
    # reports are garbage that looks like a Hohmann departure with an absurd
    # arrival. Verifying the flight time catches that.
    if not math.isfinite(t_got) or abs(t_got - dt) > 0.01 * dt:
        return None
    g = A * math.sqrt(y / mu)
    f = 1.0 - y / r1
    gdot = 1.0 - y / r2
    # Vectors: r1 along +x, r2 at dtheta.
    r1v = (r1, 0.0)
    r2v = (r2 * cos_d, r2 * sin_d)
    v1 = ((r2v[0] - f * r1v[0]) / g, (r2v[1] - f * r1v[1]) / g)
    v2 = ((gdot * r2v[0] - r1v[0]) / g, (gdot * r2v[1] - r1v[1]) / g)
    # Circular planet velocities (prograde, perpendicular to radius).
    vc1 = math.sqrt(mu / r1)
    vc2 = math.sqrt(mu / r2)
    vp1 = (0.0, vc1)
    vp2 = (-vc2 * sin_d, vc2 * cos_d)
    vinf1 = math.hypot(v1[0] - vp1[0], v1[1] - vp1[1])
    vinf2 = math.hypot(v2[0] - vp2[0], v2[1] - vp2[1])
    energy = (v1[0] ** 2 + v1[1] ** 2) / 2.0 - mu / r1
    a_km = -mu / (2.0 * energy) if abs(energy) > 1e-12 else float("inf")
    return vinf1, vinf2, a_km


def best_fast_transfer(r1_au, r2_au, tof_years, r_park_km=118232.0):
    """Sweep transfer angle for the lowest TOTAL mission dv at fixed flight time.

    Minimising departure C3 alone picks a transfer that arrives too fast to
    capture; the capture burn is part of the bill, so the sweep has to see it.
    """
    best = None
    d = 15.0
    while d <= 345.0:
        if abs(math.sin(math.radians(d))) > 1e-4:
            sol = lambert(r1_au, r2_au, d, tof_years)
            if sol is not None and math.isfinite(sol[0]):
                total = (leo_departure_dv(sol[0])
                         + capture_dv("Saturn", sol[1], r_park_km)[0])
                if best is None or total < best[2]:
                    best = (d, sol, total)
        d += 0.25
    return best


def leo_departure_dv(v_inf):
    """Oberth-correct burn from circular LEO onto a hyperbola with this v_inf."""
    return math.sqrt(v_inf * v_inf + V_ESC_LEO ** 2) - V_LEO


def max_turn_deg(body, v_inf):
    """Maximum hyperbolic deflection from a single closest-safe flyby."""
    _, mu, radius, alt = BODY[body]
    rp = radius + alt
    e = 1.0 + rp * v_inf * v_inf / mu
    return math.degrees(2.0 * math.asin(1.0 / e)), e


def capture_dv(body, v_inf_arrive, r_park_km):
    """Burn to drop from arrival hyperbola to a circular park orbit."""
    _, mu, radius, _ = BODY[body]
    rp = r_park_km
    v_hyp = math.sqrt(v_inf_arrive ** 2 + 2.0 * mu / rp)
    v_circ = math.sqrt(mu / rp)
    return v_hyp - v_circ, v_hyp, v_circ


def prop_fraction(dv, isp):
    ve = isp * G0 / 1000.0
    return 1.0 - math.exp(-dv / ve)


def rule(title):
    print("\n" + "=" * 76)
    print(title)
    print("=" * 76)


def main():
    rule("1. MINIMUM-ENERGY REFERENCE: Hohmann, Terra -> Saturn")
    dv1, dv2, tof = hohmann(1.0, 9.53707)
    dep = leo_departure_dv(dv1)
    print(f"  heliocentric departure dv : {dv1:7.3f} km/s  (v_inf from Terra)")
    print(f"  burn from 300 km LEO      : {dep:7.3f} km/s  (Oberth-corrected)")
    print(f"  heliocentric arrival dv   : {dv2:7.3f} km/s")
    print(f"  time of flight            : {tof:7.3f} yr")
    cap, vh, vc = capture_dv("Saturn", dv2, 60000.0 + 58232.0)
    print(f"  capture into 60k km park  : {cap:7.3f} km/s "
          f"(v_hyp {vh:.3f} -> v_circ {vc:.3f})")
    total_h = dep + cap
    print(f"  TOTAL (LEO -> Saturn orbit): {total_h:7.3f} km/s")
    for name, isp in ISP.items():
        print(f"    propellant fraction @ {name:8s} Isp {isp:6.0f}s : "
              f"{prop_fraction(total_h, isp)*100:6.2f}%")

    rule("2. THE FILM'S NUMBER: Terra -> Saturn in fixed flight time (Lambert)")
    print(f"  {'tof yr':>7s} {'dth':>6s} {'v_inf dep':>10s} {'C3':>9s} "
          f"{'LEO burn':>9s} {'v_inf arr':>10s} {'capture':>9s} {'TOTAL':>9s}")
    rows = []
    for tof in (6.047, 5.0, 4.0, 3.0, 2.0, 1.5, 1.0):
        best = best_fast_transfer(1.0, 9.53707, tof)
        if best is None:
            print(f"  {tof:7.3f}  no solution")
            continue
        dth, (vinf1, vinf2, a_km), _tot = best
        dep_f = leo_departure_dv(vinf1)
        cap_f, _, _ = capture_dv("Saturn", vinf2, 60000.0 + 58232.0)
        total = dep_f + cap_f
        rows.append((tof, total))
        print(f"  {tof:7.3f} {dth:5.1f}d {vinf1:10.3f} {vinf1**2:9.1f} "
              f"{dep_f:9.3f} {vinf2:10.3f} {cap_f:9.3f} {total:9.3f}")
    print("\n  New Horizons, the highest-energy launch ever flown: C3 = 158.")
    print("  Propellant fraction at the one-year solution:")
    tof1 = best_fast_transfer(1.0, 9.53707, 1.0)
    if tof1 is not None:
        dth, (vinf1, vinf2, _), _t2 = tof1
        total_f = leo_departure_dv(vinf1) + capture_dv(
            "Saturn", vinf2, 60000.0 + 58232.0)[0]
        for name, isp in ISP.items():
            pf = prop_fraction(total_f, isp)
            mr = 1.0 / (1.0 - pf) if pf < 1.0 else float("inf")
            print(f"    {name:8s} Isp {isp:6.0f}s : {pf*100:7.3f}%   "
                  f"mass ratio {mr:12.1f}")

    rule("3. THE LADDER: heliocentric legs, and what the assists can buy")
    legs = [("Terra", "Mars"), ("Mars", "Jupiter"), ("Jupiter", "Saturn")]
    tot_dv, tot_t = 0.0, 0.0
    print(f"  {'leg':20s} {'dv_dep':>8s} {'dv_arr':>8s} {'tof yr':>8s}")
    for a_name, b_name in legs:
        d1, d2, t = hohmann(BODY[a_name][0], BODY[b_name][0])
        tot_dv += d1 + d2
        tot_t += t
        print(f"  {a_name+' -> '+b_name:20s} {d1:8.3f} {d2:8.3f} {t:8.3f}")
    print(f"  {'propulsive total':20s} {tot_dv:8.3f} km/s over {tot_t:.2f} yr")
    print("\n  Maximum single-flyby deflection at each rung:")
    print(f"  {'body':10s} {'v_inf':>8s} {'max turn':>10s} {'ecc':>8s} "
          f"{'dv equiv':>10s}")
    for body, vinf in (("Mars", 5.0), ("Jupiter", 9.0), ("Saturn", 5.5)):
        turn, e = max_turn_deg(body, vinf)
        dv_equiv = 2.0 * vinf * math.sin(math.radians(turn) / 2.0)
        print(f"  {body:10s} {vinf:8.2f} {turn:9.2f}d {e:8.3f} "
              f"{dv_equiv:9.3f} km/s")
    print("  A Jupiter flyby is worth more free dv than the entire")
    print("  propulsive ladder above. That is why the rung exists.")

    rule("4. SATURN ARRIVAL -> TITAN")
    mu_s = BODY["Saturn"][1]
    v_titan = math.sqrt(mu_s / TITAN_A_KM)
    print(f"  Titan orbital radius      : {TITAN_A_KM:10.0f} km "
          f"({TITAN_A_KM/BODY['Saturn'][2]:.1f} Saturn radii)")
    print(f"  Titan orbital speed       : {v_titan:7.3f} km/s")
    print(f"  Titan period              : {TITAN_PERIOD_D:7.3f} d")
    print(f"  approach-side half-orbit  : {TITAN_PERIOD_D/2:7.3f} d  "
          f"<- the 'seven days'")
    # Park at Titan radius, then match Titan.
    r_park = 60000.0 + BODY["Saturn"][2]
    v_park = math.sqrt(mu_s / r_park)
    at = 0.5 * (r_park + TITAN_A_KM)
    vp = math.sqrt(mu_s * (2.0 / r_park - 1.0 / at))
    va = math.sqrt(mu_s * (2.0 / TITAN_A_KM - 1.0 / at))
    t_raise = math.pi * math.sqrt(at ** 3 / mu_s) / 86400.0
    print(f"  raise park -> Titan orbit : {abs(vp-v_park):7.3f} + "
          f"{abs(v_titan-va):7.3f} = {abs(vp-v_park)+abs(v_titan-va):.3f} km/s")
    print(f"  transfer time             : {t_raise:7.3f} d")
    v_esc_titan = math.sqrt(2.0 * TITAN_MU / (TITAN_R + 1200.0))
    print(f"  Titan escape at 1200 km   : {v_esc_titan:7.3f} km/s")
    print(f"  Titan capture is cheap: shallow well, thick atmosphere.")
    print(f"  Aerocapture is available here and nowhere else on the route.")

    rule("5. WINDOWS")
    def syn(pa, pb):
        return 1.0 / abs(1.0 / pa - 1.0 / pb)
    P = {k: BODY[k][0] ** 1.5 for k in BODY}
    P["Neptune"] = 30.06896 ** 1.5
    for pair in (("Terra", "Mars"), ("Terra", "Jupiter"), ("Terra", "Saturn"),
                 ("Jupiter", "Saturn"), ("Saturn", "Neptune")):
        print(f"  {pair[0]+' / '+pair[1]:22s} synodic {syn(P[pair[0]], P[pair[1]]):8.4f} yr")
    print(f"  {'2 x Saturn/Neptune':22s}         "
          f"{2*syn(P['Saturn'], P['Neptune']):8.4f} yr  <- 'every 70 years'")
    print(f"  {'Titan half-orbit':22s}         "
          f"{TITAN_PERIOD_D/2/365.25:8.4f} yr  = {TITAN_PERIOD_D/2:.2f} d")


if __name__ == "__main__":
    main()

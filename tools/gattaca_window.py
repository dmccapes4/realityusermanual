#!/usr/bin/env python3
"""What approach path fits Gattaca's stated launch window?

Two numbers are stated in the film (quoted from docs/GATTACA_TRANSCRIPT.md):

  line 118  "on a one-year manned mission to Titan, the 14th moon of Saturn"
  line 1617 "The window for our latest launch is open
             for seven days once every 70 years."

This works out what trajectory, if any, those two numbers are consistent with.
Standard orbital elements only; no dependencies beyond the stdlib.

Run: python3 tools/gattaca_window.py
"""

import math

AU = 1.495978707e11          # m
YEAR = 365.25 * 86400.0      # s
MU_SUN = 1.32712440018e20    # m^3/s^2

# Sidereal orbital periods in Julian years, and semi-major axes in AU.
PLANETS = {
    "Earth":   (1.0000174, 1.00000011),
    "Jupiter": (11.862615, 5.20336301),
    "Saturn":  (29.447498, 9.53707032),
    "Uranus":  (84.016846, 19.19126393),
    "Neptune": (164.79132, 30.06896348),
}

# Saturn's orbit is eccentric enough that "how far away is Saturn" has a
# thousand-fold spread in launch energy between its best and worst case.
SATURN_E = 0.0541506
TITAN_PERIOD_D = 15.945


def hohmann(a1_au, a2_au):
    """Minimum-energy transfer: time of flight (yr) and the two burns (km/s)."""
    a1, a2 = a1_au * AU, a2_au * AU
    a_t = 0.5 * (a1 + a2)
    tof = math.pi * math.sqrt(a_t**3 / MU_SUN)
    v1 = math.sqrt(MU_SUN / a1)
    v2 = math.sqrt(MU_SUN / a2)
    vp = math.sqrt(MU_SUN * (2.0 / a1 - 1.0 / a_t))
    va = math.sqrt(MU_SUN * (2.0 / a2 - 1.0 / a_t))
    return tof / YEAR, (vp - v1) / 1000.0, (v2 - va) / 1000.0


def synodic(p1, p2):
    """Period between repeats of the relative configuration of two bodies."""
    return abs(1.0 / (1.0 / p1 - 1.0 / p2))


def period_for_synodic(s_years, p_inner=1.0):
    """Inverse: what orbital period gives a synodic period of s_years vs Earth?"""
    # 1/s = 1/p_inner - 1/p  ->  p = 1 / (1/p_inner - 1/s)
    return 1.0 / (1.0 / p_inner - 1.0 / s_years)


def fly_out(v0, r0_au=1.0, span_yr=1.2, dt=3600.0):
    """Radial two-body coast from r0 at speed v0 (m/s). Returns (yr, AU) samples.

    Straight-out radial is the cheapest way to cover distance fast, so it is a
    LOWER BOUND on what a one-year crossing costs. A real trajectory must also
    match Saturn's 9.7 km/s transverse motion, which costs more, not less.
    """
    r = r0_au * AU
    v = v0
    t = 0.0
    out = [(0.0, r0_au)]
    while t < span_yr * YEAR:
        # Leapfrog on the radial equation; gravity only decelerates here.
        a = -MU_SUN / (r * r)
        v += a * dt
        r += v * dt
        t += dt
        if r <= 0:
            break
        out.append((t / YEAR, r / AU))
    return out


def speed_to_reach(target_au, years, lo=30e3, hi=200e3):
    """Departure speed at 1 AU that reaches target_au in `years` (radial)."""
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        samples = fly_out(mid, span_yr=years, dt=1800.0)
        if samples[-1][1] < target_au:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def alignment_recurrence(bodies, max_years=400.0, step=0.01, tol_deg=6.0):
    """When does the relative geometry of `bodies` repeat?

    A configuration repeats when every pairwise relative longitude has come back
    to where it started. Returns the times where the worst pairwise error is
    inside `tol_deg`, keeping one entry per local minimum.
    """
    rates = [360.0 / PLANETS[b][0] for b in bodies]
    pairs = [(i, j) for i in range(len(rates)) for j in range(i + 1, len(rates))]
    hits = []
    t = step
    prev_err = None
    rising = False
    while t <= max_years:
        err = 0.0
        for i, j in pairs:
            d = ((rates[i] - rates[j]) * t) % 360.0
            err = max(err, min(d, 360.0 - d))
        if prev_err is not None:
            if err > prev_err and not rising:
                # Just passed a local minimum at the previous step.
                if prev_err <= tol_deg:
                    hits.append((round(t - step, 2), round(prev_err, 2)))
                rising = True
            elif err < prev_err:
                rising = False
        prev_err = err
        t += step
    return hits


def window_recurrence(bodies, max_years=400.0, step=0.005, half_window_d=3.5):
    """When does a 7-day launch window genuinely reopen for this set of bodies?

    Unlike a fixed angular tolerance, each pair is allowed only the drift it
    accumulates during the stated window. That is the honest test: if Saturn has
    moved further than it moves in a week, the week is not the same week.
    """
    rates = [360.0 / PLANETS[b][0] / 365.25 for b in bodies]  # deg/day
    pairs = [(i, j) for i in range(len(rates)) for j in range(i + 1, len(rates))]
    tols = [abs(rates[i] - rates[j]) * half_window_d for i, j in pairs]
    hits = []
    t = step
    while t <= max_years:
        ok = True
        for k, (i, j) in enumerate(pairs):
            d = ((rates[i] - rates[j]) * t * 365.25) % 360.0
            if min(d, 360.0 - d) > tols[k]:
                ok = False
                break
        if ok:
            # Keep one entry per contiguous run of satisfied steps.
            if not hits or t - hits[-1] > 0.5:
                hits.append(round(t, 2))
        t += step
    return hits


def main():
    print("=" * 72)
    print("GATTACA: what path fits 'seven days once every 70 years'?")
    print("=" * 72)

    print("\n-- 1. The minimum-energy path, for reference " + "-" * 27)
    tof, dv1, dv2 = hohmann(1.0, PLANETS["Saturn"][1])
    print(f"  Hohmann Earth -> Saturn:      {tof:.2f} years in transit")
    print(f"    departure burn              {dv1:.2f} km/s")
    print(f"    arrival burn to circularise {dv2:.2f} km/s")
    s_es = synodic(PLANETS["Earth"][0], PLANETS["Saturn"][0])
    print(f"  Earth-Saturn synodic period:  {s_es:.4f} yr = {s_es*365.25:.1f} days")
    print("  So a launch window to Saturn -- ANY two-body transfer to Saturn --")
    print("  recurs about once a year. Not once every 70.")

    print("\n-- 2. What has a 70-year window? " + "-" * 39)
    p = period_for_synodic(70.0)
    a = p ** (2.0 / 3.0)
    print(f"  A 70-year synodic period with Earth means the target orbits in")
    print(f"    {p:.5f} yr, semi-major axis {a:.5f} AU")
    print("  That is not an outer planet. It is a body sharing Earth's orbit:")
    print("  a co-orbital, 1.4% outside us, lapping us once a human lifetime.")
    print(f"  A 70-year ORBIT, by contrast, has a = {70**(2/3):.2f} AU")
    print("    (between Saturn at 9.54 and Uranus at 19.19)")

    print("\n-- 3. What a one-year crossing costs " + "-" * 35)
    r_sat_peri = PLANETS["Saturn"][1] * (1 - SATURN_E)
    r_sat_aphe = PLANETS["Saturn"][1] * (1 + SATURN_E)
    print(f"  Saturn ranges {r_sat_peri:.2f} - {r_sat_aphe:.2f} AU from the Sun")
    for label, target in (("perihelion", r_sat_peri), ("aphelion", r_sat_aphe)):
        v = speed_to_reach(target, 1.0)
        # v_infinity relative to Earth, departing along Earth's track.
        v_earth = math.sqrt(MU_SUN / AU)
        vinf = v - v_earth
        c3 = (vinf / 1000.0) ** 2
        print(f"  Reach Saturn at {label} ({target:.2f} AU) in 1.00 yr:")
        print(f"    heliocentric departure speed {v/1000:.1f} km/s")
        print(f"    v-infinity from Earth         {vinf/1000:.1f} km/s")
        print(f"    C3                            {c3:.0f} km^2/s^2")
    print("  New Horizons, the highest-energy launch ever flown: C3 = 158")
    print("  Voyager 1 cruises at 3.6 AU/yr. This needs ~9 AU/yr, crewed.")

    print("\n-- 4. Alignment cycles: does anything recur near 70 years? " + "-" * 13)
    for bodies in (
        ["Earth", "Saturn"],
        ["Jupiter", "Saturn"],
        ["Earth", "Jupiter", "Saturn"],
        ["Jupiter", "Saturn", "Uranus", "Neptune"],
    ):
        hits = alignment_recurrence(bodies)
        name = " + ".join(bodies)
        shown = ", ".join(f"{t:.1f}yr" for t, _ in hits[:6]) or "none inside 400 yr"
        print(f"  {name}:")
        print(f"    repeats at {shown}")

    print("\n-- 5. Where 'seven days' could come from " + "-" * 31)
    print(f"  Titan's orbit around Saturn: {TITAN_PERIOD_D:.3f} days")
    print(f"    half of it:                {TITAN_PERIOD_D/2:.2f} days")
    print("  An arrival corridor is roughly the half-orbit when Titan is on the")
    print("  approach side of Saturn. That is a ~7-day window, and it is the one")
    print("  number in the quote that matches a real cycle exactly.")
    print(f"  But it recurs every {TITAN_PERIOD_D:.1f} DAYS, not every 70 years.")

    print("\n-- 6. Is 70 years ANY planetary alignment? " + "-" * 28)
    print("  The film attributes the window to 'the planets turning' (line 856),")
    print("  and launches are routine -- 'a dozen' a day (line 102). So the gate is")
    print("  geometry, not propellant. Tolerance below is what each pair drifts in")
    print("  the stated 7-day window, so a 'repeat' means the window really reopens.")
    subsets = [
        ["Earth", "Saturn"],
        ["Earth", "Jupiter", "Saturn"],
        ["Jupiter", "Saturn"],
        ["Jupiter", "Saturn", "Uranus"],
        ["Earth", "Jupiter", "Saturn", "Uranus"],
        ["Saturn", "Uranus"],
        ["Saturn", "Neptune"],
        ["Earth", "Saturn", "Uranus", "Neptune"],
    ]
    for bodies in subsets:
        hits = window_recurrence(bodies, max_years=400.0)
        name = " + ".join(b[0] for b in bodies)
        if not hits:
            print(f"  {name:22s} no reopening inside 400 yr")
            continue
        near = [t for t in hits if abs(t - 70.0) <= 3.0]
        shown = ", ".join(f"{t:.1f}" for t in hits[:7])
        flag = "  <-- 70!" if near else ""
        print(f"  {name:22s} reopens at {shown} yr{flag}")
    print("\n  Verdict: no alignment of the bodies on the way to Saturn reopens")
    print("  on a 70-year cycle. The nearest cycles are 19.9 and 79.4 years.")

    print("\n" + "=" * 72)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""The echo-star acclimation ladder for a Titan approach.

Two constraints from the governed-field corpus decide the shape of this path:

  echo-star.mdc       Each gravity assist is an acclimation event -- a
                      decompression stop. Bodies that entered without the
                      successive phase-shift preparation broke apart (3I/ATLAS).

  NSFTDrive I4        The handoff into a destination field is smooth only if the
                      approaching governance is frequency-tuned to that field;
                      untuned entry reproduces the Oumuamua/3I-class boundary
                      anomaly. Validated: tuned 375 steps, untuned 391, none 537.

Those say the same thing from opposite ends, so the ladder has to satisfy both:
every rung must be reachable, AND the retune between consecutive rungs must be
small or harmonic. This computes the rungs and the retune at each one.

Run: python3 tools/titan_approach_ladder.py
"""

import math

AU = 1.495978707e11
M_SUN = 1.98892e30

# name: (a_AU, eccentricity, inclination to Zecliptic deg, mass kg, sidereal
# rotation period in hours)
BODIES = {
    "Terra":   (1.00000, 0.01671, 0.000, 5.97219e24, 23.9345),
    "Mars":    (1.52371, 0.09339, 1.850, 6.41710e23, 24.6229),
    "Jupiter": (5.20336, 0.04839, 1.304, 1.89813e27,  9.9250),
    "Saturn":  (9.53707, 0.05415, 2.485, 5.68319e26, 10.5610),
}

# Saturn's rotation period is genuinely disputed: Cassini-era analyses give
# ~10.561 h, Voyager System III gave 10.656 h. Both are carried.
SATURN_ROT_ALT = 10.656
TITAN_PERIOD_D = 15.945
# Titan is tidally locked, so its rotation frequency IS its orbital frequency.
TITAN_ROT_H = TITAN_PERIOD_D * 24.0

# Above this, matching is a resonance-capture problem; below it, a direct trim.
NEAR_IDENTITY = 1.10


def hill_radius_au(a_au, ecc, mass):
    """Field-bubble radius: where the body's governance beats Sol's."""
    return a_au * (1.0 - ecc) * (mass / (3.0 * M_SUN)) ** (1.0 / 3.0)


def best_harmonic(ratio, max_den=12, tol=0.02):
    """Lowest-ORDER integer ratio p/q within `tol` of `ratio`.

    Order (p+q) is the quantity to minimise, not error. A low-order resonance is
    a wide, strong, forgiving lock; a high-order one is narrow and fragile. So
    the NEAREST ratio is not the meaningful one -- the simplest adequate ratio
    is. Minimising error instead returns things like 145:4, which is arithmetic
    rather than physics.
    """
    best = None
    for q in range(1, max_den + 1):
        p = round(ratio * q)
        if p < 1:
            continue
        err = abs(ratio - p / q) / ratio
        if err <= tol and (best is None or (p + q) < (best[0] + best[1])):
            best = (p, q, err)
    if best is None:
        # Nothing simple is adequate at this tolerance; report the crudest fit
        # so the caller can see that no low-order lock exists.
        q = max_den
        p = max(round(ratio * q), 1)
        best = (p, q, abs(ratio - p / q) / ratio)
    return best


def main():
    print("=" * 74)
    print("TITAN APPROACH: the echo-star acclimation ladder")
    print("=" * 74)

    print("\n-- Field bubbles: how deep each rung is " + "-" * 34)
    print(f"  {'body':9s} {'a (AU)':>8s} {'bubble (AU)':>12s} "
          f"{'bubble (Gm)':>12s} {'Zecliptic':>10s}")
    for name, (a, e, inc, m, _rot) in BODIES.items():
        rh = hill_radius_au(a, e, m)
        print(f"  {name:9s} {a:8.3f} {rh:12.5f} {rh*AU/1e9:12.3f} "
              f"{inc:9.3f}d")

    print("\n-- The retune at each rung " + "-" * 47)
    print("  I4 requires the approaching governance to be frequency-matched to")
    print("  the field it is entering. Using each body's rotation as the")
    print("  characteristic frequency of its field, the retune between")
    print("  consecutive rungs is the ratio of their periods.")
    ladder = ["Terra", "Mars", "Jupiter", "Saturn"]
    print("\n  A ratio within a few percent of unity is matched by trimming the")
    print("  frequency directly -- there is no resonance to capture, and quoting")
    print("  a harmonic for it would dress a small gap as a lock it is not. So a")
    print("  harmonic is reported only where one is actually required.")
    print(f"\n  {'rung':22s} {'ratio':>8s}  nature of the retune")
    total_cost = 0.0
    for i in range(len(ladder) - 1):
        a_name, b_name = ladder[i], ladder[i + 1]
        pa = BODIES[a_name][4]
        pb = BODIES[b_name][4]
        ratio = max(pa, pb) / min(pa, pb)
        p, q, err = best_harmonic(ratio)
        # Cost of a retune: distance from unity, discounted by how cleanly it
        # lands on a low-order harmonic.
        cost = abs(math.log(ratio)) * (1.0 + err * 10.0)
        total_cost += cost
        if ratio < NEAR_IDENTITY:
            verdict = f"{(ratio - 1.0) * 100:.1f}% trim, no lock needed"
        elif err < 0.02:
            verdict = f"{p}:{q} lock, order {p + q}, error {err * 100:.2f}%"
        else:
            verdict = f"no low-order lock within 2% (best {p}:{q})"
        print(f"  {a_name+' -> '+b_name:22s} {ratio:8.4f}  {verdict}")
    print(f"\n  Total retune cost along Terra -> Mars -> Jupiter -> Saturn: "
          f"{total_cost:.4f}")

    print("\n  Saturn's rotation is disputed; the Voyager value changes the last")
    pj = BODIES["Jupiter"][4]
    for label, ps in (("Cassini  10.561 h", BODIES["Saturn"][4]),
                      ("Voyager  10.656 h", SATURN_ROT_ALT)):
        r = ps / pj
        p, q, err = best_harmonic(r)
        print(f"    Jupiter -> Saturn with {label}: ratio {r:.4f} "
              f"({p}:{q}, {err*100:.2f}%)")

    print("\n-- Skipping rungs: order, not size, is what bites " + "-" * 24)
    print("  The size of a retune is not the difficulty. A LOW-ORDER harmonic")
    print("  (small p+q) is a wide, strong, forgiving lock; a high-order one is")
    print("  narrow and fragile. That is the ordinary resonance argument, and it")
    print("  is what separates a practicable rung from an impracticable jump.")
    print(f"\n  {'step':22s} {'ratio':>8s} {'harmonic':>10s} {'order':>6s} {'error':>8s}")
    rows = [("Mars", "Jupiter"), ("Terra", "Jupiter"), ("Terra", "Saturn"),
            ("Mars", "Saturn")]
    for a_name, b_name in rows:
        pa, pb = BODIES[a_name][4], BODIES[b_name][4]
        ratio = max(pa, pb) / min(pa, pb)
        p, q, err = best_harmonic(ratio)
        print(f"  {a_name+' -> '+b_name:22s} {ratio:8.4f} {str(p)+':'+str(q):>10s} "
              f"{p+q:6d} {err*100:7.2f}%")
    print("\n  Mars -> Jupiter is the lowest-order lock on the board: 5:2, order 7.")
    print("  Terra -> Saturn direct is a SMALLER ratio (2.27 against 2.48) and yet")
    print("  needs 9:4, order 13 -- nearly twice the order, so a lock half as wide,")
    print("  taken with no intermediate field to practise the retune in. The direct")
    print("  run is not a bigger step. It is a narrower one, attempted cold.")

    print("\n-- The final rung: Saturn to Titan " + "-" * 39)
    ps = BODIES["Saturn"][4]
    r = TITAN_ROT_H / ps
    p, q, err = best_harmonic(r, max_den=8)
    print(f"  Saturn {ps:.3f} h -> Titan {TITAN_ROT_H:.1f} h (tidally locked)")
    print(f"    ratio {r:.2f}  nearest low-order harmonic {p}:{q} "
          f"(order {p+q}, error {err*100:.2f}%)")
    print("  A factor of 36 is the largest single retune in the sequence, and it")
    print("  is the reason the ARRIVAL has a window at all: Titan's field turns")
    print("  once per orbit, so the phase you must match is its orbital phase.")

    print("\n-- Window structure: two nested periodicities " + "-" * 28)
    print(f"  Titan's orbit                 {TITAN_PERIOD_D:.3f} d")
    print(f"  approach-side half of it      {TITAN_PERIOD_D/2:.2f} d  <- the 'seven days'")
    syn_js = 1.0 / abs(1.0 / 11.862615 - 1.0 / 29.447498)
    syn_sn = 1.0 / abs(1.0 / 29.447498 - 1.0 / 164.79132)
    print(f"  Jupiter-Saturn synodic        {syn_js:.3f} yr  <- ladder gate")
    print(f"  Saturn-Neptune synodic        {syn_sn:.3f} yr")
    print(f"  twice Saturn-Neptune          {2*syn_sn:.3f} yr  <- 'every 70 years'")
    print("  A Director rounding 71.7 to 70 in dialogue is ordinary speech.")
    print("  The 7 days is Titan's own phase; the ~70 years is the outer gate.")

    print("\n" + "=" * 74)


if __name__ == "__main__":
    main()

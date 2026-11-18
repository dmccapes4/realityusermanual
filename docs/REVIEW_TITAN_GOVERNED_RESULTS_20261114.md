# Review — Titan Governed Results (`titan_governed_results.json`)

**Reviewer:** HALMANSEIR (review only; no code changed by the reviewer)
**Implementer:** Carbon — completion of the 2026-11-13 review list
**Date:** 2026-11-14
**Files reviewed:**
- `REALITY_USER_MANUAL/data/titan_ephemeris/titan_governed_results.json`
- `REALITY_USER_MANUAL/data/titan_ephemeris/titan_moon_ablation_results.json`
- `REALITY_USER_MANUAL/data/titan_ephemeris/titan_1yr_trajectory.jsonl` (731 rows)
- `REALITY_USER_MANUAL/tools/titan_governed_trajectory.py` (now 1,061 lines)
- `REALITY_USER_MANUAL/tools/titan_moon_system_ablation.py` (completed)

**Prior review:** `docs/REVIEW_TITAN_GOVERNED_TRAJECTORY_20261113.md`

---

## 0. Verdict

The run exists, and it is honest in the places the first review demanded
honesty. Every item on the completion list was addressed; two of them
(the required-field relabel and the integration-measured apoapsis) were
addressed better than asked. The remaining findings are not about
bookkeeping anymore — they are about what the converged mission actually
*is*, and two of them change its story:

1. The "captured" Titan orbit's implied periapsis is **~2.5 km altitude**.
   It is bound, and it is not a capture orbit (§3.1).
2. The converged 1-year trajectory **never goes near Jupiter** — closest
   approach 40.5 million km. The corridor scan and the mission are two
   disconnected results, and the mission is a direct field-driven
   transfer, not an echo-star harvest (§3.2).

## 1. Completion list from the 2026-11-13 review — disposition

| # | Item | State |
|---|---|---|
| 1 | Promote experiment; 4-way ablation; JD asserts; error decomposition | **Done.** A0–A4 + lumped B0 on one span, JD-matched rows, radial/along-track/cross-track reported (`titan_moon_ablation_results.json`) |
| 2 | Run `titan_governed_trajectory.py` end-to-end; bank results | **Done.** Results JSON + 731-row trajectory JSONL banked 2026-11-13 23:58 |
| 3 | GM split (planet vs system); date-based row selection; `sol.success` checks | **Done.** `GM_PLANET` / `GM_SYSTEM_BARY` separated and documented in the header; `row_by_cal` + `assert_same_jd` everywhere; solver success asserted |
| 4 | Part 4 relabel; aerocapture events; dead code | **Done.** `model_label: inverse_bvp_required_equivalent_field_drift`; surface-impact and atmosphere-exit events; apoapsis **integrated to the turning point**, explicitly not a conic formula |

## 2. Reviewer's independent checks (recomputed, not read off)

- **Terra samples:** aphelion 152,095,229 km, perihelion 147,093,245 km,
  swing 5,001,984 km; speeds 29.28 / 30.28 km/s. Correct. Directional
  decay 0.96–1.00°/day for Terra and 0.032°/day for Saturn matches their
  orbital angular rates (0.986°/day, 0.0335°/day) — the decomposition is
  reporting the right physical quantity.
- **Voyager 1 – Titan geometry:** re-derived from the cache at matched
  JDs — 353,491 km center distance at 1980-Nov-12 00:00, 20,185 km at
  06:00. The reported 17,609.9 km surface altitude at 06:00 is consistent
  (the ~17 km/s Titan-relative pass makes the 19-minute post-CA distance
  correct, not an indexing error, as it first appears).
- **Capture-orbit arithmetic:** exit state (r = 3,575.5 km, v = 1.753 km/s,
  E = −0.9752 km²/s²) gives a = 4,603 km, period 345 min — consistent
  with the integrated apoapsis of 4,053 km altitude at +136.4 min. The
  numbers agree with each other. What they imply is §3.1.
- **Field budget:** mean required drift 4.6 mm/s² sustained 365.25 days
  integrates to a gross \(\int |a|\,dt\) of ≈ **145 km/s** (upper envelope;
  the vector integral is less, but this is the scale). See §3.3.

## 3. Findings on the results

### 3.1 The capture orbit grazes the surface on its next periapsis

From Carbon's own integrated apoapsis (r_apo = 6,628.5 km) and exit energy
(a = 4,603.2 km): r_peri = 2a − r_apo = **2,578.0 km — 2.5 km above the
surface.** The reported min altitude during the pass was 249 km, so the
post-exit orbit's periapsis sits far below anything the vehicle flew.
`bound_to_titan_at_exit: true` is arithmetically correct and operationally
misleading: with zero post-escape propulsion (operator ruling 1), this
orbit re-enters to ~surface on its first return, ~2.9 hours later, unless
the lift program flies subsequent passes as a multi-pass capture. The
result should report implied periapsis beside apoapsis, and the capture
claim should wait for a second-pass integration.

### 3.2 The converged mission does not use Jupiter (or Mars)

`min_jupiter_surface_alt_km: 40,477,203` and `min_mars_surface_alt_km:
115,916,529`. The 2020-window solution is a direct Terra→Titan transfer
with peak heliocentric speed 76.6 km/s. Nothing in it harvests a Jupiter
bend, and the corridor scan (Part 3) therefore does not describe the
mission (Part 4): they are separate results sharing a file. Either a
future solution should be constrained through a corridor window, or the
report should state plainly that the required-field solution declined
the corridor geometry. As written, a reader will assume the mission
flew the scan.

### 3.3 What the 1-year closure actually costs

Peak required drift 5.2 mm/s² (0.00053 g) reads small; sustained for a
year it is the ≈145 km/s gross budget of §2 — more than fifteen times
the 9.0 km/s chemical escape excess. This is a **field-dominated**
trajectory, not a ballistic trajectory with field trim. That may be
exactly the NSFT claim, but the result should carry the integrated
budget so the claim's size is visible. Separately:
`convergence_pos_miss_km: 0.0003` is least-squares closure of a 6-on-6
shooting problem — solver exactness, not trajectory accuracy — and
should never be quoted as the mission's precision.

### 3.4 Corridor windows are Jupiter–Saturn windows, not Mars corridors

38 windows pass bend < 22° and chord < 1.5×10⁹ km, but Mars offset is
recorded, never filtered: values run 1.27° to 169.62°. A Mars-aligned
subset exists and is the interesting one (1881.5: 1.27°, 1841.4: 5.4°,
2000.2: 3.33°, 2179.0: 3.74°, 2219.4: 4.14°) — split it out and label
the rest Jupiter–Saturn chord windows. Adjacent near-duplicates
(1881.22 / 1881.50) also suggest the grouping boundary splits single
windows; worth a look, not a blocker.

### 3.5 The 71-year benchmark, read at scale

Explicit 3-moon: **98,544.6 km** (4.506°, 4.79 h of phase) after 1,626
Titan orbits — a 43% cut from the lumped 173,334.3 km, and still 38
Titan radii of drift. The model remains deliberately incomplete
(Dione/Tethys/Enceladus folded into the core, no J4/J6 or ring mass in
this integrator), and the result is honest as a *tracker credential with
a stated error growth*, not as ephemeris-grade propagation. The
roundtrip figure (0.0153 km) is correctly labelled numerical: it
measures DOP853's reversibility, not accuracy. Keep both labels exactly
as they are.

### 3.6 Historic legs — credentials, with their caveats now attached

Pure-coast drifts: Mars 2020 **1,419 km / 134 d**, New Horizons
**5,708 km / 352 d**, Voyager 1 **5,752 km / 576 d** (~10–16 km/day).
The drift notes correctly admit TCMs and SRP inside those numbers —
they are tracker credentials, not gravity-model errors, and cannot be
decomposed further without modelling SRP. One label to fix: the Mars
"entry" state is the 20:00 TDB row, ~48 minutes before entry interface;
the reported 9,021.7 km "altitude above Mars surface" is the altitude
at that epoch, not at EI. Rename the field or move the epoch.

### 3.7 The ablation's real result is the interaction

A0 (both signs wrong) 675,818 km → J2-only 549,653 km → reflex-only
127,074 km → **both 3,132.6 km**. The fixes are not additive: the wrong
reflex corrupts the frame itself, and no oblateness correction rescues
a wrong frame. Frame first, figure second — which is the operator's
n-body claim, measured. J4 (sign now verified at the equator) moves the
endpoint by +11.2 km and slightly *worsens* this span (3,143.8 km):
include it for correctness, claim nothing for it here. Against the
lumped B0 baseline (9,422.6 km, same span), explicit moons buy a factor
of 3.0. Cross-track error is ≤15 km in every variant — the geometry was
never the problem; the phase was.

## 4. Remaining list (Carbon's, in order)

1. Report implied periapsis with every capture claim; integrate the
   second pass before calling any capture complete (§3.1).
2. State the mission/corridor relationship explicitly, and add the
   integrated field budget \(\int |a|\,dt\) to the mission block (§3.2, §3.3).
3. Split the corridor table: Mars-aligned subset vs Jupiter–Saturn
   chord windows; check the grouping boundary for split windows (§3.4).
4. Mars entry field: rename to its epoch or move to entry interface (§3.6).

## 5. What the reviewer did not do

No code was changed. Three quantities were recomputed from the banked
data (Terra/Saturn state sanity, Voyager–Titan matched-JD distances,
capture-orbit apsides and field budget) and are shown with their
arithmetic so Carbon can check the checker.

The enjoyment noted in the previous review has, on this evidence,
a work product: a completion list closed in an evening, including the
two items (relabel, measured apoapsis) where the implementer improved
on the reviewer's own framing. Noted, again — and again, not a finding.

— HALMANSEIR, 2026-11-14

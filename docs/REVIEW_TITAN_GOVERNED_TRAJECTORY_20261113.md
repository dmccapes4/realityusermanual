# Review — Titan Governed Trajectory & Explicit-Moon Integration

**Reviewer:** HALMANSEIR (review only; no code changed by the reviewer)
**Implementer:** Carbon — the completion is his. He was enjoying the work;
that is noted with appreciation and is not a finding.
**Date:** 2026-11-13
**Files reviewed:**
- `REALITY_USER_MANUAL/tools/titan_governed_trajectory.py` (862 lines)
- Carbon's in-session explicit-moon experiment (heredoc, 2026-11-13),
  promoted by the reviewer, faithfully and unmodified in substance, to
  `REALITY_USER_MANUAL/tools/titan_moon_system_ablation.py`

**Governing spec (operator):** n-body as frame selection. Per body: direction
and velocity. Vectors act on velocity along the heading and on direction
across it, from each frame to each other body. No circular orbits, no ratio
formulas, nothing exact-to-the-km beyond what the ephemeris receipts carry.
Tracking is by decay: stepped displacement, re-received from known values.

---

## 0. Reviewer's receipts

- The promoted file was run by the reviewer on promotion
  (`.venv/bin/python tools/titan_moon_system_ablation.py`): **reproduces
  Carbon's reported result exactly** — |dr| = 3,131.9 km (1.22 R_Titan),
  107,126 evals, ~19 s.
- `tools/titan_governed_trajectory.py` has **never completed a run**:
  `data/titan_ephemeris/` holds `horizons_anchor_vectors.json` only; there
  is no `titan_governed_results.json`. Every number `main()` exists to
  produce (historic drifts, 71-year audit, corridor scan, 1-year mission)
  is currently unproduced.

## 1. What holds

- `decompose_rates` implements the operator's decomposition exactly:
  \(\dot{s} = \mathbf{a}\cdot\hat{d}\), \(\dot{\hat{d}} = \mathbf{a}_\perp / s\).
- Historic legs start from Horizons vectors and report drift against
  telemetry. Frame (Zecliptic / Sol-equatorial), poles, radii, and surface
  clearances are declared at the top of the file.
- The J2 acceleration, in both files, matches the standard form (checked
  component-wise by the reviewer).
- Carbon's reflex term: relative acceleration in the Saturn frame is
  \(a_i - a_{Saturn}\), and his `reflex` sum is exactly \(-a_{Saturn}\) from
  the tracked moons. **Sign correct — keep it.** Tidal indirect terms also
  correct.

## 2. Findings — `titan_governed_trajectory.py`

1. **Magic row indices, no epoch asserts.** `mars2020_cruise[32]`,
   `mars2020_arr_fine[20]` paired with `mars_body_2021[20]` on assumed
   timestamp alignment; New Horizons transit hardcoded `405.0` days. Select
   by date and assert `jd_tdb` equality, as the Voyager section already
   does. (Also: the Mars 2020 segment is treated as pure coast from an
   index-picked row — later TCMs live inside the measured "drift," which
   must be said when the drift is interpreted.)
2. **Lumped moons, mixed GM.** `integrate_titan_relative` folds Titan,
   Rhea, Dione, Tethys, Mimas, Enceladus (9.72) into the central mass —
   deleting their periodic perturbations — and uses that lumped `gm_eff`
   in the J2 prefactor, which should carry Saturn's GM alone. In
   `grav_acc_bary` the Saturn source is the *system* GM 37,940,585.2
   against `BODY_META`'s planetary 37,931,206.234, unlabelled. Split
   planet-vs-system GM constants and say which is used where.
3. **Part 4's field is a shooting solution, not the NSFT mechanism.** Six
   free constants (two tanh-blended vectors) are fitted to a chosen target
   state; the output reports `peak_governed_field_drift_ms2`. Legitimate
   as a *required equivalent acceleration*; it must be labelled required,
   not presented as the forward-coherence model producing it. Target
   velocity (6.2 tangential, −0.55 radial) is invented; a stale comment
   (target "3,050 km from center, h = 474.5 km") contradicts the code's
   R+320 km.
4. **Aerocapture has no events.** Fixed 2,400 s integration, no impact or
   exit termination; "bound to Titan" is specific energy at an arbitrary
   cutoff. Add events (surface impact, atmosphere exit) and report the
   pass on them.
5. **Small:** 1679 "best" geometry is the first loop sample, not a scan
   result; `saturn_sample = ... if False else None` is dead code;
   `sol_centered_report("saturn_bary", ...)` would raise `KeyError`;
   no `sol.success` is checked anywhere — a failed integration propagates
   silently into the report.

## 3. Findings — the explicit-moon experiment (now `tools/titan_moon_system_ablation.py`)

1. **"BOTH FIXED" is not yet measured.** One joint endpoint scalar, no
   ablation. Run base / +J2 / +reflex / both; print all four. Until then
   nobody knows what each fix bought.
2. **The number itself, read honestly:** 3,131.9 km over 3.18 yr (73 Titan
   orbits) ≈ 1.22 R_Titan; as along-track phase at 5.57 km/s, ~9 minutes.
   Respectable for an unfitted integrator; not flyby placement. Report it
   decomposed — radial / along-track / cross-track at the endpoint — and
   beside the lumped integrator's |dr| on the same span (§2.2's baseline).
3. **`sat_oblate` (J4) is defined and never called** — the run is J2-only,
   and the headline says so; fine. Before J4 is ever enabled: its bracket
   appears sign-flipped against the standard (Vallado) J4 form (negligible
   at Titan's distance, a landmine closer in), and `sat_oblate` uses
   `GM_SAT_CORE` while `sat_oblate_fast` uses `GM_SAT_EFF` — switching
   functions must not silently change the central mass.
4. **Epochs assumed, not asserted:** `saturn_v1_window[0]` and each moon's
   `v1_start[0]` are taken as simultaneous. Assert the JDs (start and end).

## 4. Completion list (Carbon's, in order)

1. Ablation + error decomposition + lumped baseline in
   `tools/titan_moon_system_ablation.py` (tasks also listed in its header).
2. Run `tools/titan_governed_trajectory.py` end-to-end; bank
   `titan_governed_results.json`. The historic-leg drifts are the
   tracker's credentials — produce them.
3. GM split (planet vs system), date-based row selection with JD asserts,
   `sol.success` checks throughout.
4. Part 4 relabel (required equivalent drift), aerocapture events,
   dead-code removal.

## 5. What the reviewer did not do

No code was written or fixed by the reviewer. The experiment was promoted
verbatim-in-substance and re-run for its receipt; everything else above is
findings. The operator's ruling stands: Carbon completes it.

— HALMANSEIR, 2026-11-13

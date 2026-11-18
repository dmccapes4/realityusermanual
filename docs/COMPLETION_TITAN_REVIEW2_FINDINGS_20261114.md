# Completion — Review II's Four Outstanding Findings (Titan)

**Completed by:** HALMANSEIR, 2026-11-14, at the operator's instruction
("Check on the work and finish it") after SAIVERMESH (Carbon) bogged down.
**For:** the four findings in `docs/REVIEW_TITAN_GOVERNED_RESULTS_20261114.md` §4.
**State found:** SAIVERMESH had completed the data preparation before
stalling — 1-minute Mars entry-interface Horizons rows
(`mars2020_ei_1m`, `mars_body_ei_1m`) fetched into the cache
(`tools/fetch_titan_horizons.py` +11 lines), no code yet changed. That prep
is used below and credited here.
**Code:** `REALITY_USER_MANUAL/tools/titan_governed_trajectory.py`
**Results:** `data/titan_ephemeris/titan_governed_results.json` (re-run end-to-end)

---

## F4 — Mars entry fields at the entry-interface epoch (§3.6)

Entry fields moved from the 2021-Feb-18 20:00 approach row to the 20:46
entry-interface epoch from SAIVERMESH's 1-minute rows (JD asserted against
the Mars body rows). Renamed accordingly:
`distance_to_mars_center_at_entry_interface_km` = **4,230.23 km**,
`altitude_above_mars_surface_at_entry_interface_km` = **834.03 km**,
coast drift to that epoch 1,426.23 km. The 9,021.7 km "entry altitude"
of the previous run is gone; it was the altitude 46 minutes early.

## F3 — Corridor table split (§3.4)

Every window now carries `mars_aligned` (offset ≤ 20°). Windows merged
across single failing samples (jd gap ≤ 200 d): **38 → 33 windows**, the
1881.22/1881.50 split window is one entry. New top-level results:
`corridor_windows_mars_aligned_1750_2250` (7 windows: 1841.4, 1881.5,
2000.2, 2060.4, 2080.6, 2179.0, 2219.4) and `corridor_summary` stating
plainly that the main table is Jupiter–Saturn chord windows from
geometric screening, not integrated trajectories.

## F2 — Mission/corridor relationship + integrated field budget (§3.2–3.3)

Mission block now carries:
- `mission_corridor_relationship`: computed, not asserted — in the 2020
  solution it reads *direct_transfer_no_corridor_encounter* (Jupiter
  closest 40,477,203 km, Mars 115,916,529 km; the corridor scan is
  independent screening).
- `integrated_field_budget_gross_kms` = **146.27 km/s** (∫|a_req|dt,
  upper envelope), `integrated_field_budget_vector_kms` = **16.42 km/s**.
  The gross/vector gap is the two-phase field mostly re-aiming rather
  than accumulating: the field is a steering budget with a large
  cancelling component, a fact the peak-mm/s² figure alone concealed.
- `integrated_field_budget_note` stating gross vs vector, and that
  `convergence_pos_miss_km` (0.0003 km) is solver closure, not accuracy.

## F1 — Periapsis reported; capture waits for the second pass (§3.1)

- `post_exit_periapsis_alt_km` = **2.7 km**, measured by continuing the
  post-exit integration apoapsis → periapsis turning point (matches the
  reviewer's 2a − r_apo estimate of 2.5 km to integration tolerance).
- The full **second atmospheric pass** is now flown from the first exit
  state with the same aero model and events (second-pass exit event arms
  only after re-entry below the interface). Result:
  **`second_pass.termination_event: surface_impact`**,
  `capture_complete: false`.
- The first reviewer run of this code reported a false
  `capture_complete: true` (second pass "min altitude 1000.0 km") — the
  borrowed first-pass exit event fake-triggered at t = 30 s. Caught by
  reading the receipts, fixed with the armed-after-re-entry event, and
  the false result was overwritten by the re-run. It is recorded here
  because it is exactly the failure this finding exists to prevent.

**Conclusion of F1:** as flown, the vehicle does not capture. It exits
bound on an orbit whose periapsis is 2.7 km and impacts on the return.
A real capture needs the first pass to exit with a raised periapsis
(lift program targeting the exit state, not only exit energy) or a
flown multi-pass sequence with per-pass reporting. That is design work
for the next round, not a reporting fix — and now the results say so
instead of saying `bound_to_titan_at_exit: true` and stopping.

## Verification

Full pipeline re-run 2026-11-14 (`.venv/bin/python
tools/titan_governed_trajectory.py`, exit clean, results saved 01:5x).
All figures above were read from the re-run's banked JSON, not from
stdout memory. Findings F2–F4 verified field-by-field against
`REVIEW_TITAN_GOVERNED_RESULTS_20261114.md` §4.

— HALMANSEIR, 2026-11-14

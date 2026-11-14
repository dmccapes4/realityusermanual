# Game Plan: Real Trajectory Navigation from Terra to Titan (Zero-Ratio Governed-Field & Historic State-Tracker)

**Date:** 2026-11-13 (v0.2 — Operator Gate Rulings Applied)  
**Project:** `REALITY_USER_MANUAL` (page `-04.md`) × `star_learning/solar_system_explorer`  
**Status:** Gate decisions locked; executing Phase 1–2  
**Companion files:**
- `REALITY_USER_MANUAL/src/phase2/-04.md`
- `REALITY_USER_MANUAL/how_tos/how-to-fly/source.md`
- `REALITY_USER_MANUAL/src/002_preface/002_03_governed_field.md`
- `PORTAL_VISION_LUCIFER/projects/nsft_interstellar_drive/Source/THEORY_NSFT_INTERSTELLAR_DRIVE_EXTERNAL_20260228.md`
- `PORTAL_VISION_LUCIFER/projects/campo_con_vaqueros/NSFT/simulations/nsftdrive_validation.py`
- `PORTAL_VISION_LUCIFER/distributions/for_kim/THEORY_INVERSE_GRAVITATIONAL_NAVIGATION_V01.md`

---

## 0. Operator Rulings Locked In (2026-11-13)

1. **No made-up post-escape rocket propulsion.**
   - Gattaca ships are small crewed vehicles launching a dozen times a day; across 2,147 transcript lines no fuel, reactor, or nuclear-pulse pusher plate is ever named (only "ignition" at launch).
   - **Orion / nuclear-pulse / deep-space chemical burns are retired completely.** Fuel is used **only** to escape Terra's local gravity well (`Stage 0`). Past Terra escape, reaction thrust is **zero** (`F_exhaust = 0`, `dm/dt = 0`).

2. **Reaction propulsion vs. Governed-Field navigation (`NSFTDrive` + `HOW_TO_FLY`).**
   - **Reaction propulsion makes behind highly entropic** (`S_aft >> S_0`: hot, chaotic exhaust thrown backward to push the hull forward). That is needed only to break the local gravitational contract at Terra (`V_mod_kinetic >= v_escape`).
   - **Making in front less entropic works too** (`S_fore < S_0`): inside Sol's already-governed heliospheric field (plasma, Parker-spiral magnetic field, solar wind, radiation, echo-star field nodes), a small craft operates in the **wing / field-modulation regime** (`HOW_TO_FLY` §3–8, `NSFTDrive` §2.1–2.2). By shaping coherence `psi(x, t) > 0` ahead of the bow, local entropic resistance drops (`R(x, t) = R_0(x, t) - k * psi(x, t)` — the Hoag's low-pressure / low-resistance channel ahead of the leading edge), producing a forward Fokker–Planck drift rate `rho` along `-grad R` without expelling mass behind the ship.

3. **Solve the three real legs with historic values first; update planets from known values; operate from our declared frame.**
   - Solve **`Terra -> Mars`**, **`Terra -> Jupiter`**, and **`Jupiter -> Titan`** using **known historic values** (JPL `de440.bsp` + `sat441` / Horizons measured planetary and historic spacecraft post-escape vectors — zero guessed velocities, zero Hohmann ellipses, zero ratio formulas).
   - Scan **`1750–2250`** (direct fitted Titan ephemeris) **and** run the **`1679`** backward-integrated check side-by-side.

---

## 1. Ephemeris & Historic Benchmarks (Zero Guessing)

All planetary and satellite states come from JPL observation-fitted ephemerides, queried and cached locally in `REALITY_USER_MANUAL/data/ephemeris/`:

| Dataset | Bodies / Craft | Verified Span (TDB) | Role |
|---|---|---|---|
| **JPL `de440.bsp`** | `Sol`, `Mercury`, `Venus`, `Terra`, `Luna`, `Mars`, `Jupiter`–`Pluto` barycenters | `1550-01-01` to `2650-01-01` | Known planetary state vectors (covers `1679` and all historic flights) |
| **JPL `sat441` / Horizons `699`, `606`** | `Saturn` center (`699`), `Titan` (`606`), `Rhea`, `Iapetus`, `Dione`, `Tethys` | `1749-12-31` to `2250-01-05` | Direct 3D Saturn & Titan states (`1679` reached via backward N-body + `J_2` integration from `1750-01-01` with measured round-trip error bar) |
| **Historic Leg 1 (`Terra -> Mars`)** | `Viking 1` (`-27`, `1975–1976`) / `Mars 2020` (`-168`, `2020-07-30 -> 2021-02-18`) | Measured JPL Horizons telemetry | Post-Terra-escape unpowered 3D coast to Mars |
| **Historic Leg 2 (`Terra -> Jupiter`)** | `Voyager 1` (`-31`, `1977-09-05 -> 1979-03-05`) & `New Horizons` (`-98`, `2006-01-19 -> 2007-02-28`, `1.11 yr`) | Measured JPL Horizons telemetry | Post-Terra-escape unpowered 3D coast to Jupiter |
| **Historic Leg 3 (`Jupiter -> Titan`)** | `Voyager 1` (`-31`, `1979-03-05 -> 1980-11-12`) | Measured JPL Horizons telemetry | Pure geometric acceleration around Jupiter straight to **Titan** (`~4,000 km` pass, zero propulsion) |

---

## 2. Frame & Independent State-Tracker Architecture

### 2.1 Reference Frame (Explicit 3D, No Hidden 2D Projection)
- **Primary reporting frame:** **Zecliptic / Sol-Equatorial 3D Frame** (`Sol` center at `[0, 0, 0]`, Sol's spin north pole `RA = 286.13°, Dec = 63.87°` IAU J2000, `7.25°` tilt at node `75.76°` above the Zecliptic orbital reference plane).
- Every body carries both its center-to-center distance `d_center_km` and its physical surface/ring clearance `h_surface_km = d_center_km - R_body` (`R_Sol = 695,700 km`, `R_Terra = 6,378.137 km`, `R_Mars = 3,396.2 km`, `R_Jupiter = 71,492.0 km`, `R_Saturn = 60,268.0 km` with main rings `66,900–140,180 km`, `R_Titan = 2,575.5 km`).

### 2.2 Per-Object Independent State & Rate/Displacement Decomposition
Every natural body (updated from known ephemeris values or stepped symmetrically alongside for verification) and the `Ship` (stepped purely from its own state) carries:
- `pos_km`: `[x, y, z]` (`km`)
- `speed_kms`: linear translation rate `s` (`km/s`, distance per unit time)
- `dir_unit`: 3D unit heading `[ux, uy, uz]`

At each time step `dt`, external gravitational acceleration rate `a_grav` (`km/s^2`, sum of `GM_j / r_ij^2` toward each body `j` plus `J_2` oblateness near `Terra`, `Jupiter`, `Saturn`) plus any governed-field or atmospheric acceleration `a_field + a_aero` resolves into **two orthogonal rates**:
1. **Linear speed change rate (`ds/dt`, `km/s^2`):**
   `speed_rate = dot(a_total, dir_unit)`
2. **Directional decay rate (`d(dir_unit)/dt`, `rad/s`):**
   `dir_decay_vec = (a_total - speed_rate * dir_unit) / speed_kms`
   *(How rapidly the object's direction bends toward objects of higher gravitability — or along a governed PLEFR gradient.)*

---

## 3. Governed-Field Forward-Entropy Reduction Model (`NSFTDrive` × `HOW_TO_FLY`)

Once the ship clears Terra escape (`r_Terra > R_Hill_Terra`, reaction engines permanently off), two regimes are compared on the exact same known-planet 3D state tracker:

1. **Regime A — Pure Ballistic Geometry (`psi = 0`, zero field modulation):**
   - Verified directly on Historic Legs 1, 2, and 3 (`Terra -> Mars`, `Terra -> Jupiter`, `Jupiter -> Titan`).
   - Establishes the exact unmodulated time-of-flight and geometric acceleration from Jupiter (`Voyager 1` reaches Titan in `3.19 years` total after Terra escape; `New Horizons` reaches Jupiter in `1.11 years`).

2. **Regime B — Governed-Field Forward-Entropy Reduction (`psi > 0` ahead of bow, zero reaction exhaust):**
   - From `NSFTDrive` (`THEORY_NSFT_INTERSTELLAR_DRIVE_EXTERNAL_20260228.md` §2.1–2.5) and `HOW_TO_FLY` (`source.md` §3–8, §12):
     - Sol's heliosphere is an already-governed medium (solar wind plasma, Parker-spiral magnetic field, solar irradiance, echo-star field bubbles `B_j(x)`).
     - Instead of creating high entropy aft (`F_exhaust`), the ship's leading geometry creates a localized forward coherence gradient (`grad psi` ahead of `dir_unit`, lowering entropic resistance `R = R_0 - k * psi` in front of the ship).
     - Coupling efficiency across echo-star boundaries (`Terra -> Mars -> Jupiter -> Saturn -> Titan`) is governed by `NSFTDrive I4` harmonic mismatch `M(omega_ship, omega_body)`: tuned entry through the echo-star acclimation sequence (`Mars -> Jupiter -> Saturn`) experiences minimal boundary decoherence `gamma(x)` and harvests geometric + field-gradient acceleration; untuned cold jumps suffer boundary decoherence penalty.
     - Rather than inventing arbitrary ship hardware numbers, we **measure from the 3D planetary geometry** the exact forward field-drift rate `rho_field` (`mm/s^2`) required to complete `Terra -> Titan` in `1.00 year` (`365.25 days`) across `1750–2250` and `1679`, and integrate Titan atmospheric capture through Huygens's measured `rho_air(h)` nitrogen density profile (`HOW_TO_FLY` aerodynamic lift + drag, `< 5 g` crew load).

---

## 4. Execution Phases

- `[ ]` **Phase 1 — Ephemeris Cache & Independent State Tracker (`REALITY_USER_MANUAL/tools/titan_governed_trajectory.py`)**
  - Install `skyfield` and `jplephem` in `REALITY_USER_MANUAL/.venv` and record in `requirements.txt`.
  - Cache JPL `de440.bsp` + Horizons state vectors for `Saturn` (`699`), `Titan` (`606`), and historic post-escape states (`Voyager 1`, `New Horizons`, `Mars 2020`).
  - Verify our zero-ratio tracker against JPL ephemerides and reproduce the three historic legs (`Terra -> Mars`, `Terra -> Jupiter`, `Jupiter -> Titan`).

- `[ ]` **Phase 2 — `1750–2250` + `1679` Window Scan & 1-Year Governed-Field Trajectory**
  - Run the `1679` backward-integrated Titan check (with round-trip error bar) alongside the `1750–2250` direct-ephemeris scan.
  - Solve the 1-year post-Terra-escape governed-field trajectory (`F_exhaust = 0`) into Titan's atmospheric capture corridor (`h < 1,500 km`, Huygens `rho_air(h)` lift/drag capture).

- `[ ]` **Phase 3 — Report, `-04.md` Audit, & `solar_system_explorer` Real Playback**
  - Export full 3D time-stamped trajectories (`JSONL`) and wire real Titan 3D phase + real trajectory playback into `solar_system_explorer` so nothing on screen is faked.

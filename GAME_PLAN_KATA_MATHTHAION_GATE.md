# GAME_PLAN — ΚΑΤΑ ΜΑΘΘΑΙΟΝ Phase 2 gate

**Filed:** 2026-11-06  
**Trigger:** Phase 2 transition on the website (`realityusermanual.dylanmccapes.systems`)  
**Name lock:** `docs/library/personal/ΚΑΤΑ ΜΑΘΘΑΙΟΝ` (extensionless; that spelling only — θθ, not τθ)  
**Destination stills:** `video/minus10b/stills/hall_indefinite.jpg` (ink hall — preferred web match) and `video/minus10/stills/hall_01.png` (photo hall — optional alternate)  
**Story anchors:** `src/phase2/-10.md`, `src/phase2/-10b.md`; theta-as-gate already spoken on −35 ("The gates were theta. He saw them open.")

---

## 0. Beats (what the viewer sees)

1. **Title hold.** `ΚΑΤΑ ΜΑΘΘΑΙΟΝ` lands large, centered, on a dark or cream field. No hallway yet.
2. **Cat leaves.** `ΚΑΤΑ` resolves into a cat (ink, STYLE_LOCK). The cat walks **left** and exits frame. The remaining word is `ΜΑΘΘΑΙΟΝ`.
3. **Double-θ centers.** `ΜΑΘΘΑΙΟΝ` recenters so the two thetas (`ΘΘ`) sit on the optical center.
4. **Gates open.** The two Θ glyphs open outward as doors — circle becomes aperture, crossbar becomes leaf / hinge. Gap grows.
5. **Suck-through.** When the aperture is large enough that the vanishing point of the Phase 2 hallway fills it, POV is pulled through. Hard cut or dolly into the hallway plate. Land in Phase 2 (listen desk / phase index — decide at wire).

Duration target: ~6–10 s. Skip-able. Play once per session (localStorage), or always on the Phase 2 entry control.

---

## 1. Tools first (do not skip)

Build order is tools → assets → timeline → page mount. Do not render cat or code the suck until the tool stack below exists and has been dry-run.

### 1.1 Typography tool — Greek at display size

| Need | Why | Candidate |
|------|-----|-----------|
| A web font with full polytonic / at least capital Κ Α Τ Μ Θ Ι Ο Ν | Wrong Θ = wrong joke | Survey: **Gentium Plus**, **Source Sans 3**, **Noto Serif**, **EB Garamond** — pick one that keeps Θ round and heavy at 120–200 px |
| Measurement helper | Center on ΘΘ, not on the word bounding box | Small script: `tools/measure_kata_glyphs.py` (Pillow + font file) → writes `web/gate/glyph_metrics.json` with per-glyph advances and the ΘΘ mid-gap x |

**Deliverable before anything else:** `glyph_metrics.json` for the chosen font at the planned display size. If ΘΘ cannot be isolated as two drawable boxes, the gate morph dies.

### 1.2 Vector gate tool — Θ → door

| Need | Why | Candidate |
|------|-----|-----------|
| Editable Θ as SVG paths (left leaf, right leaf, hinge) | CSS text cannot "open" | Hand-trace or FontForge/Inkscape export of Θ → `web/gate/theta_gate.svg` |
| Morph timeline | Open outward, not explode | Prefer **SVG + CSS/SMIL** or a tiny path-lerp in JS. Avoid Lottie unless an existing Lottie pipeline appears. No new heavy runtime. |
| Aperture mask | Hallway must show *through* the open ΘΘ | SVG `<mask>` or canvas clip; hallway image behind |

**Deliverable:** static SVG of closed ΘΘ and open ΘΘ at the same viewBox. If closed/open do not share topology, redesign before coding motion.

### 1.3 Cat asset tool — already in-repo

| Need | Why | Tool |
|------|-----|------|
| Transparent ink cat PNG, STYLE_LOCK | `ΚΑΤΑ` → κάτα → cat | `tools/render_stills.py` + gpt-image-1.5, `background: transparent` |
| Walk-left strip or single sprite + CSS translate | Leave left | Same render pass: side-profile cat, or 3–4 walk frames if the hold feels dead |
| Face-lock optional | Consistency with book ink | `edit_from` only if a prior cat plate exists; else fresh prompt under STYLE_PREFIX |

**Prompt seed (do not ship until tools 1.1–1.2 pass):** cartoon-realistic ink cat, cream/bone + lampblack, paper tooth, no anime eyes, full body side profile facing left, transparent background, readable silhouette at 256–512 px tall.

**Deliverable:** `web/gate/assets/kata_cat.png` (+ optional `kata_cat_walk_01..N.png`).

### 1.4 Hallway plate tool — reuse, do not re-render first

| Asset | Path | Role |
|-------|------|------|
| Ink indefinite hall | `video/minus10b/stills/hall_indefinite.jpg` | Primary destination through the gate (matches −10b / slideshow-still contract) |
| Photo hall bay | `video/minus10/stills/hall_01.png` | Alternate if ink reads too soft at full bleed |
| Fixture gleam | `video/minus10b/stills/fixture_gleam.jpg` | Optional pre-roll or post-land beat (attention on metal) |

**Tool:** `tools/gate_hallway_plate.py` — copies chosen still into `web/gate/assets/hallway.png`, crops/resizes to 1920×1080 (or site max), records vanishing-point pixel `(vx, vy)` by hand once (click or known center — these plates are one-point and centered).

**Deliverable:** `hallway.png` + `vanishing_point.json` `{ "x": …, "y": … }`. No new OpenAI spend until the ink plate fails on screen.

### 1.5 Timeline / runtime tool

| Need | Why | Candidate |
|------|-----|-----------|
| Beat clock | Text → cat → center → open → suck | Hand-rolled `requestAnimationFrame` + a `beats.json` (start_ms, end_ms, id). Mirror listen-desk cue style, not a new framework. |
| Suck-through | Scale + translate toward `(vx,vy)` while aperture expands | CSS `transform: scale()` on hallway layer **or** canvas drawImage crop. Prefer CSS until jank. |
| Reduced motion | Accessibility | `@media (prefers-reduced-motion: reduce)` → hard cut to hallway, skip morph |
| Skip | Operator / repeat viewers | Click / Esc → jump to end state |

**Do not** pull GSAP, Three.js, or Rive for v0. The hallway is a still; the joke is typography and gates. Add WebGL only if CSS scale tears.

**Deliverable:** `web/gate/beats.json` schema + a dry-run page `web/gate/index.html` that logs beat ids to the console with no art.

### 1.6 Optional audio tool (after picture locks)

| Need | Tool |
|------|------|
| Soft gate open / suck whoosh | `tools/scratch_sfx.py` or short free SFX; keep under 2 s |
| Silence is allowed | Prefer silence over a wrong sting |

No ElevenLabs for this transition unless a Narrator line is later written for it.

### 1.7 Mount tool — website integration

| Need | Tool / file |
|------|-------------|
| Page that hosts the gate | New: `web/gate/` (static) |
| Entry from Phase 1 → Phase 2 | Wire from listen desk or station directory: a single control "Enter Phase 2" that hits `/gate/` then redirects to `/listen/` (or Phase 2 shelf) on complete |
| Deploy | Existing `web/deploy` path — no new host |

**Deliverable:** one link on the listen index or station directory. Do not scatter the animation into every page film.

---

## 2. Tool checklist (gate before art)

```
[x] 1.1 Font chosen (DejaVu Serif Bold); glyph_metrics.json written
[x] 1.2 theta SVG inlined in index.html; leaves open via rotateY
[x] 1.4 hallway.png + vanishing_point.json from −10b ink still
[x] 1.5 beats.json + web/gate/index.html + gate.js/css
[x] 1.3 kata_cat.svg (ink stand-in; PNG via render_stills still optional)
[x] 1.7 Mount: station directory links → /gate/?force=1 → /hall/
[ ] 1.6 SFX only if picture needs it
```

---

## 3. Choreography (draft timings — edit after dry-run)

| t (s) | Beat id | Action |
|------:|---------|--------|
| 0.0 | `title_in` | Full string fades/scales in, large |
| 1.2 | `kata_to_cat` | ΚΑΤΑ dissolves; cat appears in its footprint |
| 1.6 | `cat_exit_left` | Cat translates left; opacity 1→1 until off-canvas |
| 2.4 | `maththaion_center` | ΜΑΘΘΑΙΟΝ slides to center on ΘΘ midpoint |
| 3.2 | `theta_open` | Left Θ opens left, right Θ opens right; hallway masked in gap |
| 5.0 | `suck` | Scale toward vanishing point; FOV collapse |
| 6.5 | `land` | Full-bleed hallway; navigate to Phase 2 |

Exact ms live in `beats.json`. Table above is the storyboard only.

---

## 4. Style lock for new art

Same as `video/STYLE_LOCK.md`: cartoon-realistic Samurai Jack ink, cream/bone midtones, lampblack, paper tooth. Cat and any redrawn Θ ornament match the −10b ink hall, **not** the photo hall, if both stay in play.

Hallway through the gate = the still itself. Do not animate flicker. Fluorescents stay scheduled.

---

## 5. Explicit non-goals (v0)

- No pygame for the website path (pygame remains video pipeline; this is browser).
- No re-render of the full −10 / −10b films for the gate.
- No Vincent in the transition (he arrives *in* Phase 2 pages).
- No agentic loop to "improve" the morph. One SVG topology, measure, ship.
- No renaming: the string is always `ΚΑΤΑ ΜΑΘΘΑΙΟΝ`.

---

## 6. Files to create (when tools pass)

```
REALITY_USER_MANUAL/
  GAME_PLAN_KATA_MATHTHAION_GATE.md          ← this file
  tools/measure_kata_glyphs.py               ← 1.1
  tools/gate_hallway_plate.py                ← 1.4
  web/gate/
    index.html
    gate.css
    gate.js
    beats.json
    glyph_metrics.json
    theta_gate.svg
    assets/
      kata_cat.png
      hallway.png
      vanishing_point.json
```

---

## 7. First working session (copy-paste order)

1. Pick font; run glyph measure; confirm ΘΘ boxes.
2. Draw/export `theta_gate.svg` closed and open.
3. Plate-copy hallway + record vanishing point.
4. Skeleton `web/gate/index.html` + `beats.json` (no cat yet).
5. Only then: render cat; wire morph; mount link.

If step 1 fails (font cannot isolate ΘΘ), stop and change font — do not invent a fake double-theta from Latin O.

# GAME_PLAN — Book grimoire (000 … 007)

**Filed:** 2026-11-06  
**Host path:** `/book/`  
**Companion:** `GAME_PLAN_EXPERIMENT_SITE.md` (chrome: left HTML / right view screen)  
**Sources:** `src/000_velora` … `src/007_mother_earth`  
**Name lock (entry):** **BΘΘΚ** — BOOK spelled with double thetas (same joke family as ΚΑΤΑ ΜΑΘΘΑΙΟΝ)

---

## 0. Participant flow (spine)

```
/book/                 →  BΘΘΚ  (pre-cover; must click)
  → cover              →  PDF cover plate + rabbit-hole URL
  → 000 Velora poem    →  left: poem HTML · right: Narration offer
  → 001 Quenya (p.42)  →  left: Quenya · right: sidereal equation helper
  → rho reversed run   →  hallway-style: one reversed word per click → translation
  → 002 Preface        →  spreads (preface + governed field)
  → 003 rho            →  intro note + reception
  → 004 Lucifer        →  left: experiment pages · right: loaves-&-fishes slideshow + verse narration
  → 005 Waldorf        →  abstraction + Merlin seed
  → 006 Crisis         →  crisis 1–3 + editor note (fracture cause)
  → 007 Mother Earth   →  geocells — real figures + high-quality conceptual plates
  → How_tos shelf      →  left: scrollable TOC + 1–2 sentence blurbs · right: how_tos HTML index
  → Manuscripts shelf  →  left: scrollable TOC + 1–2 sentence blurbs · right: manuscripts HTML index
  → Enter Phase 2      →  /gate/  (ΚΑΤΑ ΜΑΘΘΑΙΟΝ)
```

TOC / spine nav may list chapter heads **plus** the two shelf spreads (How_tos, Manuscripts) immediately before Phase 2. **Page 42 does not appear in the TOC** (existing law: `docs/TOC.md`). Quenya is reached from Velora (000 → 001); the reversed-word run follows 001. Quiet deep link for the operator is allowed.

**Why these two last:** curios who walked Mother Earth meet the operational how_tos and the venue-shaped manuscripts before the ΚΑΤΑ threshold — filter aperture, not a dashboard dump at entry.

---

## 1. Entry: BΘΘΚ (before the cover)

**Job:** Same family as the Phase 2 gate — the book announces itself as a door, not a dashboard.

| Spec | Detail |
|------|--------|
| Glyph | `BΘΘΚ` — Latin B/K, Greek ΘΘ in place of OO |
| Look | Grimoire void / parchment field; large centered word; optional mild Θ glow |
| Action | **Click the page** (the word / the leaf) → advance to **cover**. No autoplay. |
| Skip | None on first visit. Operator `?skip=1` ok. |
| Relation to gate | Sister threshold. Do not reuse the full suck-through; this is a *title leaf*, not Phase 2. |

**Files:** `web/book/bththk/` or first card in `spreads.json` with `kind: "bththk"`.

---

## 2. Cover

**Job:** The PDF cover of `REALITY_USER_MANUAL.pdf` as the facing plate.

| Leaf | Content |
|------|---------|
| Left | Short HTML: title, mischievouslittlechicken / operator mark, one line that the rabbit hole is on the facing plate |
| Right | **Cover still** extracted from the PDF cover page (or a high-res raster of it). The **rabbit-hole URL** is live and clickable: `https://sacredthebes.dylanmccapes.systems?hello-world` |

Do not rebuild the cover as HTML chrome. The PDF cover *is* the object. Click-through on the URL leaves the book (new tab). Turning the spread continues into 000.

**Tool:** `tools/book_cover_plate.py` — render PDF page 1 → `web/book/assets/cover.png`.

---

## 3. Spread contract (reminder)

```
┌──────────────────┬──────────────────┐
│  LEFT LEAF       │  RIGHT LEAF      │
│  scrollable HTML │  view screen     │
└──────────────────┴──────────────────┘
```

Poems and Quenya use the right leaf as **instrument**, not decoration.

---

## 4. Content by section

### 4.0 — BΘΘΚ + Cover
See §§1–2.

### 4.1 — `000` Velora poem (`000_velora_poem.md`)

| Leaf | Spec |
|------|------|
| Left | Poem HTML, grimoire type. Velora as written. |
| Right | **Narration offer** — play / pause control for the Velora voice reading (existing ElevenLabs / listen assets if present; else stub + generate). Poster: ink still or empty bezel with “Narration”. |

No English crib on the right. Listening is the facing plate.

### 4.2 — `001` Quenya / Page 42 (`001_quenya_poem.md`)

**Law:** Page 42 exists; it does not appear in the TOC. HTML comment in source already states the sidereal math. Comes **immediately after** Velora — before the reversed-word run.

| Leaf | Spec |
|------|------|
| Left | Quenya poem HTML. Folio stamp may read **42** even if spine omits it. |
| Right | **Sidereal equation helper** — interactive (or stepped) board that lets the participant assemble: |

```
lunar sidereal month ≈ 27.32 d
42 × 27.32 ≈ 1147.44 d
π × 365.25 ≈ 1147.5 d
⇒ 42 sidereal months ≈ π years
```

Controls: knobs / steppers for `N` months and `year_length`, live product vs `π·year`. Target highlight when `|42·27.32 − π·365.25|` is small. Do **not** print “the answer is 42” as a banner — the board *is* the pedagogy. Bitwise 7/11 note stays in source comments / a quiet footnote, not a quiz.

English translation page: **does not exist** as a separate spread (per source). The irrational pair (Velora / Quenya) is the point.

### 4.3 — Reversed-word hallway (rho definition run) — **after 001**

**Source of truth:** `src/003_rho/rho_definition_words.py` — 40 items (`?` then 39 English words, each shown **reversed**, one per step).

**Order lock:** Velora → Quenya (42) → **then** this run → translation leaf → 002.

**UX (hall-shaped, not a stacked list):**

- One word plaque on the vanishing point of a parchment / ink corridor (or the same Phase 2 hall ground desaturated into grimoire ink).
- Display = reversed (`tfird`, `yporpne`, …).
- **Next** (same control grammar as `/hall/`) advances one word.
- Optional: hold / second click reveals the upright English for that step only, then continues.
- After the last word: land on a **translation leaf** — the continuous English definition (from `docs/library/personal/rho` or the assembled sentence), then proceed to 002 Preface.

This *is* pages 2–41 of the bound joke, without putting forty TOC entries on the spine — placed after page 42 in the web spine so Quenya is not buried behind the run.

### 4.4 — `002` Preface

| Spread | Left | Right |
|--------|------|-------|
| `002_02` preface i | HTML | conceptual still (book-as-instrument / aperture) |
| `002_03` governed field | HTML | field diagram / Zecliptic-style conceptual plate (his, labelled) |

### 4.5 — `003` rho

| Spread | Left | Right |
|--------|------|-------|
| intro note | HTML | rho mark (lower-case glyph still) |
| reception | HTML | receipt / checksum still |

(The reversed-word run already taught the definition; these pages are reception and framing, not a second dictionary.)

### 4.6 — `004` Lucifer — loaves & fishes on the right

Left leaf walks `004_01` … `004_05` (experiment, Matthew 19, aslama, shav, na bean) as ordinary grimoire HTML spreads.

**Right leaf (shared facing plate for the Matthew cluster, especially while 004 is open):** a **slideshow of loaves and fishes** plus optional **Biblical verse narration**.

| Right element | Spec |
|---------------|------|
| Slideshow | Sequence of ink / conceptual plates: gathering → scarcity named → Yeshua: bring what you have → disciples present (doubt held, not confessed) → demonstration without return ask → cascade → feast. STYLE_LOCK. Source reading: `docs/library/personal/LOAVES_AND_FISHES.txt` and `PORTAL_VISION_LUCIFER/data/theories/THEORY_BIBLE_AS_OPERATOR_MANUAL_V01.md` § Loaves and Fishes. |
| Narration | Offer play of the Gospel verse(s) for the scene (Matthew feeding narrative). Separate from the operator’s commentary — verse first; his reading is in the left text / captions, not a substitute for the text. |
| Thesis in captions | Demonstration always cascades. Greek sequence (Mt 14:13–21): scarcity named → bring what you have → bless/break → disciples to crowds → all eat → leftovers. **No multiplication verb** in MorphGNT — magical bread is an inferred genre, not a narrated event. Disciples’ unspoken “this is crazy” = operator character gloss. |

Do not draw bread spawning from empty air. The feast is the cascade made visible. Read Matthew here the way the operator does: sci-fi / Logos — sworn words, dictionary-first.

### 4.7 — `005` Waldorf

| Spread | Left | Right |
|--------|------|-------|
| abstraction | HTML | Waldorf / abstraction diagram |
| Merlin seed | HTML | oak / seed plate (ties forward to −08 without spoiling Phase 2) |

### 4.8 — `006` Crisis

Crisis 1–3 + editor note. Right leaf: crisis classroom / sit-gag plates if already rendered; else ink stills of the fracture. Editor note right leaf can be a terminal-looking bezel (Gattaca hint) — still grimoire-framed.

**End of 006** is the fracture that *causes* −0. Gutter copy may say so without dumping Phase 2.

### 4.9 — `007` Mother Earth (figures required)

**Job:** High-quality conceptual images and **real figures** — not placeholders.

| Right-leaf plate ideas (minimum set) | Label |
|--------------------------------------|-------|
| Valve geocell schematic (Beringia / Sunda / North Sea shelves) | [his] diagram |
| Beringia bathymetry / land-bridge open–closed pair | [measured] figure from public bathymetry or cited map redrawn in ink |
| AMOC cartoon with hysteresis loop | [modelled] |
| Sea-level vs valve threshold (50–130 m) | [modelled] / [measured] |
| Diprotodon → landscape → CO₂ path (one pedagogical strip) | [his] |

**Build:** Prefer SVG / matplotlib exports committed under `web/book/assets/007/` plus 1–2 gpt-image conceptual plates under STYLE_LOCK. Every figure caption carries measured / modelled / his.

Left leaf: full `007_mother_earth.md` as scrollable HTML.

After 007: **not** straight to the gate — two shelf spreads (§§4.10–4.11), then **Enter Phase 2** → `/gate/`.

### 4.10 — How_tos shelf (last-but-one before Phase 2)

**Job:** Make `how_tos/index.html` reachable on the book spine without dumping the catalog at BΘΘΚ.

| Leaf | Spec |
|------|------|
| Left | **Scrollable TOC** — one row per how_to from `how_tos/data.json`. Title (humanized) + **1–2 sentence description** (blurbs derived from `description`; strip markdown headers / meta lines; keep the pedagogical sentence). Clicking a row selects it and may scroll/highlight the matching entry on the right. |
| Right | **View screen** embedding the live how_tos HTML index (`how_tos/index.html` → deployed under `/book/embed/how_tos/` or iframe to that path). Participant can search / open / threl from the right leaf as they do at the desk. |

**Kind:** `shelf_toc`. Sources of truth remain `how_tos/data.json` + `how_tos/index.html` — book leaves are generated, not hand-duplicated.

### 4.11 — Manuscripts shelf (last page before Phase 2)

**Job:** Same contract for `manuscripts/index.html` — venue-shaped science shelf, academic-dare surface after Mother Earth.

| Leaf | Spec |
|------|------|
| Left | **Scrollable TOC** — one row per manuscript from `manuscripts/data.json`. Name + venue + **1–2 sentence description**. Grade tile optional on the left (mirror index) but left stays parchment/grimoire; do not restyle the whole cyber desk onto the left leaf. |
| Right | **View screen** embedding `manuscripts/index.html` (→ `/book/embed/manuscripts/`). Source / folder / grade expand work inside the bezel. |

**Order lock:** How_tos → Manuscripts → Enter Phase 2. (How_tos first as the operational door; manuscripts as the last formal shelf before the gate. Flip only if the operator says so.)

**Gutter after manuscripts:** CTA **Enter Phase 2** → `/gate/`. Do not bury the CTA under the iframe.

---

## 5. Manifest shape

`web/book/spreads.json` (sketch):

```json
{
  "spreads": [
    { "id": "bththk", "kind": "title_gate", "glyph": "BΘΘΚ" },
    { "id": "cover", "kind": "cover", "right": { "type": "cover", "url": "/book/assets/cover.png", "link": "https://sacredthebes.dylanmccapes.systems?hello-world" } },
    { "id": "000", "title": "Velora", "html": "/book/leaves/000.html", "right": { "type": "audio", "url": "…", "label": "Narration" } },
    { "id": "001", "title": "Quenya", "folio": 42, "toc": false, "html": "/book/leaves/001.html", "right": { "type": "sidereal_board" } },
    { "id": "rho-run", "kind": "reversed_hallway", "source": "src/003_rho/rho_definition_words.py" },
    { "id": "002_02", "…": "…" },
    { "id": "004", "title": "Lucifer", "html": "/book/leaves/004_….html", "right": { "type": "slideshow", "theme": "loaves_and_fishes", "audio": "matthew_feeding_verse" } },
    { "id": "007", "title": "Mother Earth", "html": "/book/leaves/007.html", "right": { "type": "figure_set", "ids": ["beringia", "amoc", "valves"] } },
    { "id": "how_tos", "title": "How_tos", "kind": "shelf_toc", "html": "/book/leaves/how_tos.html", "right": { "type": "embed", "url": "/book/embed/how_tos/" } },
    { "id": "manuscripts", "title": "Manuscripts", "kind": "shelf_toc", "html": "/book/leaves/manuscripts.html", "right": { "type": "embed", "url": "/book/embed/manuscripts/" } },
    { "id": "enter_phase2", "kind": "cta", "label": "Enter Phase 2", "href": "/gate/" }
  ]
}
```

---

## 6. Tools (build order)

| Tool | Job |
|------|-----|
| `tools/build_book_web.py` | md → leaf HTML + `spreads.json` |
| `tools/build_book_shelves.py` | `how_tos/` + `manuscripts/` data → TOC left leaves + copy indexes into `web/book/embed/` |
| `tools/book_cover_plate.py` | PDF p.1 → `cover.png` |
| `tools/book_rho_run.py` | import `rho_definition_words.py` → runtime JSON for reversed hallway |
| `web/book/sidereal_board.js` | Quenya right-leaf equation helper |
| `tools/render_stills.py` / matplotlib | 007 figures + poem posters |
| Existing listen / audio pipeline | Velora (and optional Quenya) narration |

---

## 7. Aesthetic lock

- Grimoire: parchment, lampblack, sewn gutter, no reviewer-desk grid as the hero.
- Right leaf is always a **recessed screen** in the binding.
- rho stays lower-case in all leaf HTML.
- Page 42 never gets a TOC row.
- BΘΘΚ and ΚΑΤΑ ΜΑΘΘΑΙΟΝ are paired thresholds (book in / Phase 2 in); do not merge them into one animation.

---

## 8. Success criteria

1. Participant must click **BΘΘΚ** before seeing the cover.
2. Cover shows the real PDF cover and the sacredthebes rabbit hole.
3. Poems offer narration on the right.
4. Order: 000 → 001 (p.42) → rho reversed run → 002….
5. Quenya right leaf can be used to *find* 42 ≈ π years without a spoiler banner.
6. 004 right leaf is loaves-and-fishes slideshow + verse narration (cascade, not magic bread).
7. 007 ships with real figures and labelled conceptual plates.
8. After 007: How_tos shelf then Manuscripts shelf (TOC left + embedded index HTML right).
9. After Manuscripts: Enter Phase 2 → `/gate/`.

---

## 9. First build slice (when implementing)

1. `/book/` shell + BΘΘΚ click → cover plate.
2. 000 leaf + narration bezel (even if audio stub).
3. 001 + sidereal board v0.
4. Reversed-word hallway wired to `rho_definition_words.py` (**after** 001).
5. Stub spreads 002–003, 005–006; 004 right = loaves slideshow shell.
6. 007 figure pass (do not ship 007 with empty bezels).
7. `tools/build_book_shelves.py` → how_tos + manuscripts shelf spreads wired before the gate CTA.

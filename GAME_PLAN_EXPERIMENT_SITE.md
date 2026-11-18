# GAME_PLAN — Experiment site (full)

**Filed:** 2026-11-06  
**Host:** `realityusermanual.dylanmccapes.systems`  
**Shape:** three rooms in one site — **Book** (pre Phase 2) → **Gate** (ΚΑΤΑ ΜΑΘΘΑΙΟΝ) → **Hallway** (Phase 2)

Companion plans:
- `GAME_PLAN_BOOK_GRIMOIRE.md` — Phase 1 content (BΘΘΚ → cover → 000…007)
- `GAME_PLAN_KATA_MATHTHAION_GATE.md` — gate choreography and tool order
- `GAME_PLAN_MINUS08.md` — page film (not site chrome)
- Bind law: `src/PAGE_ORDER.md`

---

## 0. What the experiment is

A participant does not land on a dashboard. They open a **grimoire** (Phase 1 / pre Phase 2), read forward like a book, then cross a named threshold into a **corridor** that lists Phase 2 pages *into the vanishing point*. A console can be pulled up to jump by page identity. The gate between them is not a menu — it is `ΚΑΤΑ ΜΑΘΘΑΙΟΝ` opening.

```
/book/     grimoire aesthetic · Phase 1 + zero-family approach
/gate/     title → cat leaves left → ΘΘ open → suck into hall
/hall/     Phase 2 list-forward · console for jump navigation
```

Listen desk (`/listen/`), manuscript desks (`/m/`), and page HTML (`/p/`) stay. They are *rooms off the hallway*, not the spine.

---

## 1. Three aesthetics (do not mix)

| Zone | Look | Motion | Metaphor |
|------|------|--------|----------|
| **Book** | Open grimoire spread: **left leaf = scrollable HTML**, **right leaf = view screen** (stills / video for that page) | Turn spreads; left scrolls in-place; right plays or holds media | Provenance locked; reading is a physical volume with a facing plate |
| **Gate** | Cream/bone field → ink cat → SVG ΘΘ doors → ink hallway still | Scripted 6–10 s timeline; skip allowed | Threshold. κάτα / cat / according-to |
| **Hall** | Weyland-Yutani × Gattaca corridor still as ground; recessed fluorescents; no flicker | List goes **forward** (into depth), not down a feed | Indefinitely long; pages are doors / bays |

Style locks:
- Book chrome: grimoire binding, parchment gutter, lampblack rules — not the reviewer desk grid alone. PDF content keeps its own typesetting.
- Gate + Hall plates: `video/STYLE_LOCK.md` + existing −10b ink hall.

---

## 2. Information architecture

### 2.1 Book (`/book/`)

**Job:** Phase 1 and the approach to the fracture feel like opening a physical volume — one **spread per manuscript page**.

```
┌──────────────────┬──────────────────┐
│  LEFT LEAF       │  RIGHT LEAF      │
│  scrollable HTML │  view screen     │
│  for this page   │  graphics/video  │
│                  │  for this page   │
└──────────────────┴──────────────────┘
         gutter (binding)
```

| Element | Spec |
|---------|------|
| Cover | Closed grimoire: title `REALITY_USER_MANUAL`, operator mark, no Phase 2 spoiler. Opens to first spread. |
| TOC / spine nav | Chapter heads (Velora, Quenya, preface, rho, lucifer, waldorf, crisis, mother earth) **plus How_tos and Manuscripts** as the last two spreads before Phase 2. Selecting a chapter opens its first spread. |
| **Left leaf** | **Scrollable HTML** for the current page — grimoire-styled typesetting (serif, margins, lampblack on parchment). Built from `src/` markdown via `tools/build_book_web.py` / reuse `build_phase2_page_web.py` patterns. Scroll stays inside the leaf. |
| **Right leaf** | **View screen** — still image, slideshow, or video that belongs to that same page. Letterboxed in a recessed bezel (CRT / plate glass in the binding). If no media yet: empty screen with page id stamp, not a broken image. |
| Gutter | Visible binding. Prev / next spread controls in the gutter or as page-turn hit zones on the outer edges. |
| Spread = one page | Turning the spread advances the manuscript page. Left HTML and right media **swap together** — never leave a mismatched pair. |
| Manifest | `web/book/spreads.json` — `{ id, title, html, media: { type: still\|video\|slideshow, url, poster? } }` |
| End of book | After 007: **How_tos** then **Manuscripts** shelf spreads (left = scrollable TOC + 1–2 sentence blurbs; right = embedded `how_tos/index.html` / `manuscripts/index.html`). Then CTA **Enter Phase 2** → `/gate/`. See `GAME_PLAN_BOOK_GRIMOIRE.md` §§4.10–4.11. |

**Why HTML on the left:** easier to build, style, and iterate than PDF embed. The grimoire look lives in CSS (parchment, rules, folio), not in a second typesetting pipeline. Provenance remains the markdown source; the leaf is a reading surface. PDF stays available on manuscript desks (`/m/`) for reviewers who want the packet.

**Reuse:** `tools/build_phase2_page_web.py` already emits page HTML — Book left leaf can mount the same (or a book-skinned variant) in a scroll pane. Right leaf mirrors listen-desk stage behavior (still hold / video) without leaving the spread.

**Build:** `tools/build_book_web.py` emits `spreads.json` + HTML leaves + media links. Operator fills media as plates exist. v0 shell: cover + one spread with real HTML and one still.

**Not the book:** listen catalog as a list, API docs, manuscript intake desks. Colophon link only.

### 2.2 Gate (`/gate/`)

**Job:** one cool transition. See `GAME_PLAN_KATA_MATHTHAION_GATE.md`.

| Element | Spec |
|---------|------|
| Entry | Only from Book end CTA (and a debug `?force=1`) |
| Exit | On `land` beat → `/hall/` |
| Replay | `localStorage` key `rum_gate_seen`; skip control always |

### 2.3 Hall (`/hall/`)

**Job:** Phase 2 as *place*, not as a vertical blog.

| Element | Spec |
|---------|------|
| Ground | Full-bleed hallway still (`hall_indefinite` / plate from gate assets) |
| List | Pages as **stations into the corridor** — cards or door plaques stacked toward the vanishing point (CSS perspective / scale-by-index). Order = bind order from `PAGE_ORDER.md` (−0 … −35+) |
| Click | Opens `/p/{id}/` or `/listen/play.html?id=…` (film if present, else read) |
| Console | Pull-up terminal (bottom or `~` / `` ` ``). Prompt accepts page id (`-10`, `-10b` if still aliased, `vincentvision`). Completes to that page. Aesthetic: Gattaca terminal / Vincent's station — monospace on dark recessed panel |
| Escape | Console dismiss; Book link quiet in corner ("return through the gate" optional — usually one-way story) |

**List goes forward:** index 0 nearest (largest), higher indices smaller toward vanishing point. Scroll / wheel moves *into* the hall (increase depth), not a conventional top-down feed.

---

## 3. Participant flow

```
land on / or /book/
  → read grimoire (operator builds content)
  → End spread: Enter Phase 2
  → /gate/ plays ΚΑΤΑ ΜΑΘΘΑΙΟΝ
  → /hall/ corridor list
       ├─ click a bay → page film/read
       └─ pull console → jump by id
```

First visit plays the gate. Later visits may skip to `/hall/` if `rum_gate_seen` — Book CTA can still force `/gate/?force=1`.

---

## 4. Build phases

### Phase A — Spine (this session / next)

1. Full site game plan (this file).
2. Gate animation live at `/gate/` with hallway plate + ΘΘ morph + cat + redirect to `/hall/`.
3. Hall stub: forward list of Phase 2 ids from a static `hall/pages.json` + console jump.

### Phase B — Book shell (left HTML / right screen)

1. `/book/` grimoire chrome: cover, gutter, **two-leaf spread layout**.
2. Left leaf: scrollable HTML (grimoire CSS). Right leaf: media stage (still or `<video>`).
3. `spreads.json` + `tools/build_book_web.py` — one Phase 1 chapter as proof (real HTML + one still).
4. Prev/next spread keeps HTML and media paired.
5. Wire End CTA → `/gate/`.

### Phase C — Hall filled

1. Generate `hall/pages.json` from `PAGE_ORDER.md` + listen `catalog.json` (film/audio flags).
2. Perspective list polish; door plaques; current-bay highlight.
3. Console command set: `ls`, `go <id>`, `listen <id>`, `help`.

### Phase D — Deploy & harden

1. `web/deploy` includes `/book/`, `/gate/`, `/hall/`.
2. Reduced-motion paths; mobile: hall becomes horizontal swipe-forward if perspective fails.
3. No third aesthetic creep (do not restyle listen desk into grimoire).

---

## 5. Tools inventory (site-wide)

| Tool | Zone | Status |
|------|------|--------|
| `tools/measure_kata_glyphs.py` | Gate | Build with gate |
| `tools/gate_hallway_plate.py` | Gate | Build with gate |
| `tools/render_stills.py` | Gate cat | Existing |
| `tools/build_book_web.py` | Book | Not yet — emit `spreads.json` (html + media pairs) |
| `tools/build_hall_pages.py` | Hall | Not yet — emit `pages.json` from PAGE_ORDER + catalog |
| `tools/build_phase2_page_web.py` | Hall destinations | Existing |
| `tools/build_listen_desk.py` | Off-hall rooms | Existing |

---

## 6. Console grammar (Hall v0)

```
rum> help
rum> ls              # list ids in bind order
rum> go -10          # open page −10
rum> go -10b         # alias → −10b if present
rum> listen -10      # force listen desk play
rum> clear
```

Unknown id: `no station`. No shell escapes. No network from the console.

---

## 7. Explicit non-goals

- Do not replace `/listen/` with the hall — films stay on the listen desk; hall *points* at them.
- Do not put Phase 2 pages into the grimoire as chapters.
- Do not animate fluorescent flicker in the hall ground.
- Do not require login, accounts, or analytics for the experiment.
- Do not LLM-loop the CSS.

---

## 8. Success criteria

1. A stranger can feel **book → threshold → corridor** without a tutorial.
2. In the Book, left leaf scrolls as HTML and right leaf shows that page's plate/film — never mismatched.
3. The gate is memorable once; the hall is usable many times.
4. Console finds any bound page in one command.
5. Operator can fill Book spreads (pdf + media) without rewriting Gate or Hall chrome.

---

## 9. Immediate next file set (Phase A)

```
GAME_PLAN_EXPERIMENT_SITE.md          ← this file
web/gate/                             ← animation (now)
web/hall/index.html + hall.css/js     ← stub list + console
web/hall/pages.json                   ← seed from PAGE_ORDER
web/book/                             ← Phase B (shell only if time)
```

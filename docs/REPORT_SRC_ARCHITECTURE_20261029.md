# REPORT: src/ Directory Architecture
*REALITY_USER_MANUAL — technical reference*
*2026-10-29*

---

## Directory layout

```
REALITY_USER_MANUAL/
├── src/
│   ├── 000_velora/
│   │   └── 000_velora_poem.md
│   ├── 001_quenya/
│   │   └── 001_quenya_poem.md
│   ├── 002_preface/
│   │   ├── 002_02_preface_i.md
│   │   └── 002_03_governed_field.md
│   ├── 003_rho/
│   │   ├── 003_01_intro_note.md
│   │   ├── 003_02_reception.md
│   │   └── rho_definition_words.py
│   ├── 004_lucifer/
│   │   ├── 004_01_lucifer_experiment.md
│   │   ├── 004_02_matthew_19.md
│   │   ├── 004_03_aslama.md
│   │   ├── 004_04_shav.md
│   │   └── 004_05_na_bean.md
│   ├── 005_waldorf/
│   │   ├── 005_01_waldorf_abstraction.md
│   │   └── 005_02_merlin_seed.md
│   ├── 006_crisis/
│   │   ├── 006_01_crisis_page1.md
│   │   ├── 006_02_crisis_page2.md
│   │   ├── 006_03_crisis_page3.md
│   │   └── 006_04_editor_note.md
│   ├── 007_mother_earth/
│   │   └── 007_mother_earth.md
│   ├── phase2/
│   │   ├── -0.md
│   │   ├── -00.md
│   │   ├── -000.md
│   │   ├── -0000.md
│   │   ├── -04.md
│   │   ├── -05.md
│   │   │   … (sequential through -29.md)
│   │   └── -10b.md        (variant draft, not a new integer)
│   ├── PAGE_ORDER.md      (canonical bind table — source of truth)
│   ├── path_map.json      (old filename → new path, for migration reference)
│   └── form/              (print-ready assets: front/side/three_quarter images)
├── docs/                  (desk matter — not src, not book)
│   ├── TOC.md
│   ├── TOC_ERA2.md
│   ├── HOW_TO_MANIFEST.md
│   ├── HOW_TO_REPORT.md
│   ├── MANIFEST_HOW_TO_PORTALVISION_20261024.md
│   ├── ILIAD_RETELLING_20261024.md
│   ├── page_order.jsonl
│   ├── run_full_verification.sh
│   ├── PDF_ARCHITECTURE_NOTE.md
│   ├── REFLECTION_SRC_ARCHITECTURE_20261029.md
│   └── REPORT_SRC_ARCHITECTURE_20261029.md  ← this file
```

---

## Naming rules

### Book sections (pre-PHASE-2)

| Convention | Example | Rule |
|---|---|---|
| Section folder | `NNN_name/` | Three-digit zero-padded integer + underscore + lowercase name |
| File within section | `NNN_NN_title.md` | Section number + two-digit page-within-section + title |
| Single-page section | `NNN_name.md` | As above; no `pages/` subfolder until section grows |

Section numbers are sequential from `000`. They do not correspond to the PDF page
number — they correspond to the author's ordering of thematic clusters.

The book sections have no group-level name or label. They are flat in `src/`.

### PHASE 2 pages

| Convention | Example | Rule |
|---|---|---|
| Directory | `src/phase2/` | Fixed. PHASE 2 named itself; this is its folder. |
| File | `-N.md` | The identity IS the filename. No title decoration. |
| Zero-family | `-0.md`, `-00.md`, `-000.md`, `-0000.md` | Ghost labels used as filenames. |
| Draft variants | `-10b.md` | Letter suffix for variant/draft within an integer position. |

---

## Page identity system

PHASE 2 pages have two coordinate systems:

| System | Purpose | Example |
|---|---|---|
| **Ghost label** | Symbolic identity; appears at page bottom | `00`, `000`, `0000` |
| **Integer identity** | Sequential position in the negative number line | `-1`, `-2`, `-3` |
| **PDF sheet position** | Cosmetic footer; one per physical PDF page | `-7` (for `0000`) |

The filename uses the **ghost label** for the zero-family (`-0.md`, `-00.md`, etc.)
and the **integer identity** for all others (`-04.md` through `-29.md`).

The ghost label and the integer identity converge at `-0`: identity = ghost = `-0`.

---

## mischievouslittlechicken.png

The PNG stores a `tOcM` chunk: a JSON map from label string to absolute PDF page
number. Labels match the ghost column in `PAGE_ORDER.md`.

The participant resolves a label to a page by:
1. Reading the `tOcM` chunk (the joke tool), OR
2. Opening the PDF and scrolling (available from any PDF viewer without tooling).

The point is that the page position is always already available. The script in the PNG
is the joke. The chunk is the real map.

---

## PAGE_ORDER.md

Canonical bind-order table. Columns:

| Column | Content |
|---|---|
| `#` | Page identity (the number that prints on the page) |
| `Title` | Page title |
| `File` | Canonical file path relative to `src/` |
| `Was` | Previous name or alias (migration reference) |

The `File` column is the source of truth for build.py path resolution. When a file
moves, update this column and build.py together.

---

## build.py integration

`build.py` uses:

```python
SRC = os.path.join(HERE, "src")
# ...
render_md(os.path.join(SRC, "phase2/-0.md"))
render_md(os.path.join(SRC, "000_velora/000_velora_poem.md"))
```

Phase 2 pages after `0000` are assembled from `_phase2_after_0000`, a list of paths
relative to `SRC`. New PHASE 2 pages are appended to that list in bind order.

---

## What does not go in src/

- Documentation: `docs/`
- How-to source files: `how_tos/{slug}/source.md`
- Manuscripts: `manuscripts/{slug}/`
- Build tools: `tools/`
- Assets: `assets/`
- Reflections/reports (including this file): `docs/`

`src/` is exclusively manuscript source. If a file does not appear on a PDF page, it
is not in `src/`.

---

## Next free page identity

**-29** was the last page as of 2026-10-29. The next page is **-30**.
Inject at `src/phase2/-30.md` and append to `_phase2_after_0000` in `build.py`.
Update `PAGE_ORDER.md` bind table accordingly.

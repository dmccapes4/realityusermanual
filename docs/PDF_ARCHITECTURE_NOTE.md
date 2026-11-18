# PDF Architecture — Decision Pending (2026-10-29)

## Current state

Build uses ReportLab Platypus. Each page is assembled by `build.py`, which:
- Reads markdown files from `src/era1/` and `src/era2/`  
- Renders them through a hand-rolled markdown → ReportLab flowables pipeline
- Rebuilds the **entire PDF** on every call (no incremental support)

The operator noted the style is unnatural because ReportLab extracts text and renders
it as styled flowables rather than preserving the prose structure.

## The alternative

**Pandoc → LaTeX → PDF** is the natural markdown-as-PDF-code approach. Each section
produces one or more markdown files; Pandoc assembles them with YAML frontmatter and
`\newpage` delimiters. This is what `src/era1/` and `src/era2/` are now structured for.

Benefits:
- Markdown IS the page description (no Python rendering layer)
- `\newpage` = page break, `---` = section break
- Incremental: regenerate one section without rebuilding the whole PDF
- LaTeX typesetting handles ligatures, proper hyphens, footnotes natively
- Custom template (`template.tex`) controls the Weyland-Yutani × Gattaca look

## Proposed build command

```bash
pandoc \
  src/era1/000_velora/000_velora_poem.md \
  src/era1/001_quenya/001_quenya_poem.md \
  ... \
  src/era2/028_prompt_walk/028_prompt_walk_which_witch.md \
  --from markdown \
  --to pdf \
  --template tools/rum_template.tex \
  --output REALITY_USER_MANUAL.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=11pt
```

Section order comes from `PAGE_ORDER.md`. A small script reads the bind table and
generates the pandoc invocation, so only changed sections need re-rendering if using
Pandoc's intermediate `.tex` pass.

## Special pages

HTML pages (how_tos, manuscripts) remain separate deliverables. They are referenced
in the book via URL or PDF attachment. Not part of the main PDF pipeline.

## Decision required

The operator must choose:
1. **Keep ReportLab** (current) — already working, unusual style
2. **Migrate to Pandoc** (recommended) — natural prose, requires `pandoc` + `xelatex`
   installed and a template built

Run `pandoc --version` to check if pandoc is available.

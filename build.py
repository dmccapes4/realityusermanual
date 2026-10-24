"""
REALITY_USER_MANUAL — PDF builder
ReportLab Platypus. Run with .venv/bin/python build.py

Page structure:
  Front matter (roman numerals, i–):
    DEDICATION
    Preface i: How to Not Mess with Cats
    TOC (placeholder)

  Body (arabic numerals, 1–):
    p.1   — Velora poem (src/00_page1_velora.md)
    p.2–41 — blank (chapters pending)
    p.42  — Quenya poem (src/01_page42_quenya.md)
    p.43+ — chapters as written

Page 42 is not a coincidence.
"""

import sys, os, re, json, hashlib, subprocess
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Manuscript stack: FreeSerif covers Latin + Greek + Hebrew + IPA.
# Mono for code. Symbols for the intro_note landmarks (🔍 🏗️ 🧾 🌌).
_FF = "/usr/share/fonts/truetype/freefont"
pdfmetrics.registerFont(TTFont("FreeSerif",       f"{_FF}/FreeSerif.ttf"))
pdfmetrics.registerFont(TTFont("FreeSerif-Bold",  f"{_FF}/FreeSerifBold.ttf"))
pdfmetrics.registerFont(TTFont("FreeSerif-Italic",f"{_FF}/FreeSerifItalic.ttf"))
pdfmetrics.registerFont(TTFont("FreeSerif-BI",    f"{_FF}/FreeSerifBoldItalic.ttf"))
pdfmetrics.registerFont(TTFont(
    "DejaVuSansMono",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
))
pdfmetrics.registerFont(TTFont(
    "NotoSymbols",
    "/usr/share/fonts/truetype/noto/NotoSansSymbols-Regular.ttf"
))
# Keep the old names so leftover style refs do not crash.
pdfmetrics.registerFont(TTFont(
    "DejaVuBold",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
))
pdfmetrics.registerFont(TTFont(
    "DejaVuItalic",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
))

from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    PageBreak, NextPageTemplate, KeepTogether, Image
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors

# ── colours ──────────────────────────────────────────────────────────────────
INK        = colors.HexColor("#1a1a2e")   # near-black navy
ACCENT     = colors.HexColor("#4a5a8a")   # blue-slate
PALE       = colors.HexColor("#f5f3ee")   # warm off-white page
RULE_GREY  = colors.HexColor("#cccccc")

# ── page geometry ─────────────────────────────────────────────────────────────
W, H = letter
MARGIN_OUTER = 1.0 * inch
MARGIN_INNER = 1.0 * inch
MARGIN_TOP   = 1.0 * inch
MARGIN_BOT   = 1.0 * inch

# ── page number state ─────────────────────────────────────────────────────────
# merlin_arabic is stored when the Blank callback actually fires — not guessed.
_page_state = {"mode": "roman", "arabic_start": None, "merlin_arabic": None,
               "era": 1, "neg_start": None, "era2_symbolic": None}
_page_ledger = []  # one dict per physical page, written at callback time

def roman(n):
    val = [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),
           (50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]
    r = ""
    for v, s in val:
        while n >= v:
            r += s; n -= v
    return r

def page_number_str(canvas):
    pn = canvas.getPageNumber()
    mode = _page_state["mode"]
    if mode == "roman":
        return roman(pn)
    if mode == "negative":
        # Era 2: first negative page is −0, then −1, −2, …
        start = _page_state.get("neg_start") or pn
        return f"-{pn - start}"
    start = _page_state.get("arabic_start") or pn
    return str(pn - start + 1)

def _arabic(canvas):
    pn_raw = canvas.getPageNumber()
    start  = _page_state.get("arabic_start") or pn_raw
    return pn_raw - start + 1

def _record_page(canvas, template, numbered, label, ghost_labels=None, kind=None):
    _page_ledger.append({
        "seq": canvas.getPageNumber(),
        "era": _page_state.get("era", 1),
        "label": label,
        "ghost_labels": ghost_labels or [],
        "numbered": numbered,
        "template": template,
        "kind": kind or template,
        "mode": _page_state.get("mode"),
    })

_TITLE_PAGE_URL = "https://sacredthebes.dylanmccapes.systems?hello-world"
_INSCRIPTION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "assets", "title_inscription.png")
_INS_W = 4.0 * inch
_INS_H = _INS_W * (175 / 1024)   # proportional: 1024×175 source
_LINK_Y   = 0.40 * inch            # link baseline from page bottom
_IMG_GAP  = 0.10 * inch            # gap between image bottom and link top
_IMG_Y    = _LINK_Y + _IMG_GAP + 8   # +8pt ≈ font cap-height so gap is visual
_IMG_X    = W - MARGIN_OUTER - _INS_W  # flush right

# ── callbacks ─────────────────────────────────────────────────────────────────
def _front_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("FreeSerif-Italic", 9)
    canvas.setFillColor(ACCENT)
    pnum = page_number_str(canvas)
    canvas.drawCentredString(W / 2, 0.55 * inch, pnum)
    _record_page(canvas, "Front", True, pnum, kind="front")
    if canvas.getPageNumber() == 1:
        if os.path.exists(_INSCRIPTION_PATH):
            canvas.drawImage(_INSCRIPTION_PATH,
                             _IMG_X, _IMG_Y,
                             width=_INS_W, height=_INS_H,
                             preserveAspectRatio=True, mask='auto')
        canvas.setFont("FreeSerif", 8)
        canvas.setFillColor(ACCENT)
        canvas.drawRightString(W - MARGIN_OUTER, _LINK_Y, _TITLE_PAGE_URL)
    canvas.restoreState()

def _body_page(canvas, doc):
    canvas.saveState()
    label = page_number_str(canvas)
    canvas.setFont("FreeSerif-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2, 0.55 * inch, label)
    canvas.setFont("FreeSerif", 8)
    canvas.drawCentredString(W / 2, H - 0.55 * inch, "REALITY_USER_MANUAL")
    _record_page(canvas, "Body", True, label, kind="manuscript")
    canvas.restoreState()

def _blank_page(canvas, doc):
    """No number, no head. merlin_arabic is set by _MerlinMark on the seed page."""
    _record_page(canvas, "Blank", False, None, kind="unnumbered")

def _double_num_page(canvas, doc):
    """Crisis page 1: ghost (Merlin) and real, both centered."""
    canvas.saveState()
    arabic = _arabic(canvas)
    ghost  = _page_state.get("merlin_arabic") or (arabic - 1)
    canvas.setFont("FreeSerif-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2 - 0.35 * inch, 0.55 * inch, str(ghost))
    canvas.drawCentredString(W / 2 + 0.35 * inch, 0.55 * inch, str(arabic))
    canvas.setFont("FreeSerif", 8)
    canvas.drawCentredString(W / 2, H - 0.55 * inch, "REALITY_USER_MANUAL")
    _record_page(canvas, "DoubleNum", True, str(arabic),
                 ghost_labels=[str(ghost)], kind="crisis")
    canvas.restoreState()

def _split_right_page(canvas, doc):
    """Crisis page 2: real centered, ghost far bottom right."""
    canvas.saveState()
    arabic = _arabic(canvas)
    ghost  = _page_state.get("merlin_arabic") or (arabic - 2)
    canvas.setFont("FreeSerif-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2, 0.55 * inch, str(arabic))
    canvas.drawRightString(W - MARGIN_OUTER, 0.55 * inch, str(ghost))
    canvas.setFont("FreeSerif", 8)
    canvas.drawCentredString(W / 2, H - 0.55 * inch, "REALITY_USER_MANUAL")
    _record_page(canvas, "SplitRight", True, str(arabic),
                 ghost_labels=[str(ghost)], kind="crisis")
    canvas.restoreState()

def _split_left_page(canvas, doc):
    """Crisis page 3: ghost far bottom left, real centered."""
    canvas.saveState()
    arabic = _arabic(canvas)
    ghost  = _page_state.get("merlin_arabic") or (arabic - 3)
    canvas.setFont("FreeSerif-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawString(MARGIN_INNER, 0.55 * inch, str(ghost))
    canvas.drawCentredString(W / 2, 0.55 * inch, str(arabic))
    canvas.setFont("FreeSerif", 8)
    canvas.drawCentredString(W / 2, H - 0.55 * inch, "REALITY_USER_MANUAL")
    _record_page(canvas, "SplitLeft", True, str(arabic),
                 ghost_labels=[str(ghost)], kind="crisis")
    canvas.restoreState()

def _poem_page(canvas, doc):
    """Poem pages: page number only, no running head."""
    canvas.saveState()
    label = page_number_str(canvas)
    canvas.setFont("FreeSerif-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2, 0.55 * inch, label)
    _record_page(canvas, "Poem", True, label, kind="poem")
    canvas.restoreState()

def _neg_page(canvas, doc):
    """Era 2: negative labels from −0.
    Draws only the negative label. If the page has a symbolic designation
    (00 / 000 / 0000), _Era2SymbolMark draws it directly on the same canvas
    after flowables are laid — which is reliable regardless of page-fill state.
    """
    if _page_state.get("neg_start") is None:
        _page_state["neg_start"] = canvas.getPageNumber()
        _page_state["mode"] = "negative"
        _page_state["era"] = 2
    canvas.saveState()
    label = page_number_str(canvas)   # e.g. "-0", "-1", "-2"
    canvas.setFont("FreeSerif-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2, 0.44 * inch, label)
    canvas.setFont("FreeSerif", 8)
    canvas.drawCentredString(W / 2, H - 0.55 * inch, "REALITY_USER_MANUAL")
    _record_page(canvas, "Neg", True, label, kind="era2")
    canvas.restoreState()

# ── styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, parent="Normal", **kw):
    kw.setdefault("textColor", INK)
    return ParagraphStyle(name, parent=base[parent], **kw)

STYLES = {
    "word_page": S("word_page","Normal", fontName="FreeSerif-Bold", fontSize=48,
                  leading=56, alignment=TA_LEFT, textColor=INK,
                  spaceBefore=0, spaceAfter=0),

    "poem":     S("poem",   "Normal", fontName="FreeSerif-Italic", fontSize=11,
                  leading=18, alignment=TA_LEFT,
                  leftIndent=0.8*inch, spaceAfter=0),

    "poem_div": S("poem_div","Normal", fontName="FreeSerif",    fontSize=9,
                  leading=14, alignment=TA_CENTER, textColor=ACCENT,
                  spaceBefore=14, spaceAfter=14),

    "title":    S("title",  "Normal", fontName="FreeSerif-Bold", fontSize=26,
                  leading=32, alignment=TA_CENTER, spaceBefore=0,
                  spaceAfter=0.25*inch),

    "subtitle": S("subtitle","Normal", fontName="FreeSerif-Italic", fontSize=13,
                  leading=18, alignment=TA_CENTER, textColor=ACCENT,
                  spaceAfter=0.4*inch),

    "ded":      S("ded",    "Normal", fontName="FreeSerif-Italic", fontSize=13,
                  leading=22, alignment=TA_CENTER, spaceBefore=1.5*inch,
                  spaceAfter=0.25*inch),

    "ded_plain":S("ded_plain","Normal",fontName="FreeSerif",    fontSize=11,
                  leading=16, alignment=TA_CENTER, spaceAfter=0.15*inch),

    "ded_sig":  S("ded_sig","Normal", fontName="FreeSerif-Italic", fontSize=11,
                  leading=16, alignment=TA_RIGHT,  spaceAfter=0,
                  rightIndent=1.5*inch, spaceBefore=0.4*inch),

    "h1":       S("h1",     "Normal", fontName="FreeSerif-Bold", fontSize=16,
                  leading=22, spaceBefore=0.35*inch, spaceAfter=0.12*inch),

    "h2":       S("h2",     "Normal", fontName="FreeSerif-Bold", fontSize=12,
                  leading=16, spaceBefore=0.28*inch, spaceAfter=0.08*inch),

    "body":     S("body",   "Normal", fontName="FreeSerif",     fontSize=11,
                  leading=16, alignment=TA_JUSTIFY, spaceAfter=0.09*inch),

    "body_c":   S("body_c", "Normal", fontName="FreeSerif",     fontSize=11,
                  leading=16, alignment=TA_CENTER, spaceAfter=0.09*inch),

    "meta":     S("meta",   "Normal", fontName="FreeSerif-Italic", fontSize=9,
                  leading=13, textColor=ACCENT, spaceAfter=0.05*inch),

    "toc_h":    S("toc_h",  "Normal", fontName="FreeSerif-Bold", fontSize=14,
                  leading=20, spaceBefore=0.5*inch, spaceAfter=0.3*inch,
                  alignment=TA_CENTER),

    "toc_empty":S("toc_empty","Normal",fontName="FreeSerif-Italic", fontSize=11,
                  leading=16, alignment=TA_CENTER, textColor=ACCENT,
                  spaceBefore=0.5*inch),

    "code":     S("code",   "Normal", fontName="DejaVuSansMono", fontSize=8.5,
                  leading=11, leftIndent=0.4*inch, spaceBefore=4,
                  spaceAfter=4, alignment=TA_LEFT),
}

def P(text, style="body"):
    """Paragraph with XML-safe text."""
    text = _safe(text)
    return Paragraph(text, STYLES[style])

def _safe(t):
    """Escape bare & and handle <sub>/<sup> passthrough."""
    t = re.sub(r'&(?!(?:amp|lt|gt|apos|quot|#);)', '&amp;', t)
    return t

# ── poem loader ───────────────────────────────────────────────────────────────
def load_poem(path):
    """Load a .md poem file, strip comment blocks, return list of Flowables."""
    with open(path) as f:
        raw = f.read()
    # strip HTML comments
    raw = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL).strip()
    flowables = []
    for line in raw.split("\n"):
        line = line.rstrip()
        if line == "---":
            flowables.append(P("—", "poem_div"))
        elif line == "":
            flowables.append(Spacer(1, 6))
        else:
            flowables.append(P(line, "poem"))
    return flowables

# ── markdown-lite renderer ────────────────────────────────────────────────────
def render_md(path):
    """Render a simple markdown file to Flowables. Handles # ## | - ** ` and fenced code."""
    from reportlab.platypus import Preformatted
    with open(path) as f:
        lines = f.readlines()
    flowables = []
    in_table = False
    table_rows = []
    in_code = False
    code_lines = []

    def flush_code():
        nonlocal code_lines, in_code
        if code_lines:
            # render each line as a code paragraph
            flowables.append(Spacer(1, 4))
            for cl in code_lines:
                flowables.append(Paragraph(
                    '<font name="DejaVuSansMono">' + cl.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') + '</font>',
                    STYLES["code"]))
            flowables.append(Spacer(1, 4))
        code_lines.clear()
        in_code = False

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            in_table = False
            return
        from reportlab.platypus import Table, TableStyle
        data = []
        for row in table_rows:
            data.append([Paragraph(_md_inline(c.strip()), STYLES["body"])
                         for c in row])
        t = Table(data, hAlign='LEFT', colWidths=[2.0*inch, 2.2*inch, 2.0*inch])
        t.setStyle(TableStyle([
            ('FONTNAME',  (0,0), (-1,0), 'FreeSerif-Bold'),
            ('FONTSIZE',  (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (-1,-1), INK),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [PALE, colors.HexColor("#ebebeb")]),
            ('BOX',       (0,0), (-1,-1), 0.5, RULE_GREY),
            ('INNERGRID', (0,0), (-1,-1), 0.25, RULE_GREY),
            ('VALIGN',    (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING',(0,0), (-1,-1), 4),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ]))
        flowables.append(t)
        flowables.append(Spacer(1, 8))
        table_rows = []
        in_table = False

    for line in lines:
        line = line.rstrip("\n")

        # fenced code blocks
        if line.strip().startswith('```'):
            if in_code:
                flush_code()
            else:
                if in_table:
                    flush_table()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        # table rows
        if '|' in line and line.strip().startswith('|'):
            cells = [c for c in line.strip().strip('|').split('|')]
            if all(re.match(r'\s*[-:]+\s*$', c) for c in cells):
                continue  # separator row
            in_table = True
            table_rows.append(cells)
            continue
        else:
            if in_table:
                flush_table()

        if line.startswith('# '):
            flowables.append(P(_md_inline(line[2:]), "h1"))
        elif line.startswith('## '):
            flowables.append(P(_md_inline(line[3:]), "h2"))
        elif line.startswith('- ') or line.startswith('* '):
            flowables.append(P("• " + _md_inline(line[2:]), "body"))
        elif line.startswith('> '):
            flowables.append(P("<i>" + _md_inline(line[2:]) + "</i>", "body"))
        elif line.startswith('---'):
            flowables.append(Spacer(1, 6))
            flowables.append(P("—" * 20, "body_c"))
            flowables.append(Spacer(1, 6))
        elif line.strip() == '':
            flowables.append(Spacer(1, 6))
        else:
            flowables.append(P(_md_inline(line), "body"))

    if in_table:
        flush_table()
    if in_code:
        flush_code()
    return flowables

def _md_inline(t):
    """Convert **bold**, *italic*, `code` to ReportLab XML."""
    t = _safe(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', t)
    def _code_span(m):
        inner = m.group(1)
        # Mono lacks Hebrew/Greek; keep those in the manuscript face.
        if re.search(r'[\u0370-\u03FF\u0590-\u05FF]', inner):
            return inner
        return f'<font name="DejaVuSansMono">{inner}</font>'
    t = re.sub(r'`(.+?)`', _code_span, t)
    return t

# ── document assembly ─────────────────────────────────────────────────────────
HERE   = os.path.dirname(os.path.abspath(__file__))
SRC    = os.path.join(HERE, "src")
OUT    = os.path.join(HERE, "REALITY_USER_MANUAL.pdf")

def _write_ledgers(here):
    """Merge callback metadata with per-page text. Append-only JSONL."""
    texts = []
    try:
        raw = subprocess.check_output(
            ["pdftotext", "-layout", OUT, "-"], text=True, errors="replace"
        )
        texts = raw.split("\f")
    except (subprocess.CalledProcessError, FileNotFoundError):
        texts = []
    spacing = {
        "font": "FreeSerif", "size": 11, "leading": 16,
        "align": "justify", "margin_in": 1.0,
    }
    e1, e2 = [], []
    for meta in _page_ledger:
        seq = meta["seq"]
        text = texts[seq - 1].strip() if 0 < seq <= len(texts) else ""
        rec = {
            **meta,
            "text": text,
            "assets": [],
            "spacing": spacing,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        (e2 if rec.get("era") == 2 else e1).append(rec)
    def dump(path, rows):
        with open(path, "w") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    dump(os.path.join(here, "era1_pages.jsonl"), e1)
    dump(os.path.join(here, "era2_pages.jsonl"), e2)

def build():
    _page_ledger.clear()
    _page_state.update({"mode": "roman", "arabic_start": None,
                        "merlin_arabic": None, "era": 1, "neg_start": None})
    doc = BaseDocTemplate(
        OUT,
        pagesize=letter,
        title="REALITY_USER_MANUAL",
        author="mishcievouslittlechicken",
        leftMargin=MARGIN_INNER,
        rightMargin=MARGIN_OUTER,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOT,
    )

    fw = W - MARGIN_INNER - MARGIN_OUTER
    fh = H - MARGIN_TOP - MARGIN_BOT

    front_frame = Frame(MARGIN_INNER, MARGIN_BOT, fw, fh, id="front")
    body_frame  = Frame(MARGIN_INNER, MARGIN_BOT, fw, fh, id="body")
    poem_frame  = Frame(MARGIN_INNER, MARGIN_BOT, fw, fh, id="poem")
    blank_frame = Frame(MARGIN_INNER, MARGIN_BOT, fw, fh, id="blank")

    templates = [
        PageTemplate(id="Front",      frames=[front_frame], onPage=_front_page),
        PageTemplate(id="Body",       frames=[body_frame],  onPage=_body_page),
        PageTemplate(id="Poem",       frames=[poem_frame],  onPage=_poem_page),
        PageTemplate(id="Blank",      frames=[blank_frame], onPage=_blank_page),
        PageTemplate(id="DoubleNum",  frames=[body_frame],  onPage=_double_num_page),
        PageTemplate(id="SplitRight", frames=[body_frame],  onPage=_split_right_page),
        PageTemplate(id="SplitLeft",  frames=[body_frame],  onPage=_split_left_page),
        PageTemplate(id="Neg",        frames=[body_frame],  onPage=_neg_page),
    ]
    doc.addPageTemplates(templates)

    story = []

    # ── FRONT MATTER ──────────────────────────────────────────────────────────
    _page_state["mode"] = "roman"

    story.append(NextPageTemplate("Front"))

    # Half-title / title page — title/penname top-aligned
    # Image + link are drawn on canvas at bottom-right (stele-style)
    story.append(Spacer(1, 0.3 * inch))
    story.append(P("REALITY_USER_MANUAL", "title"))
    story.append(P("mishcievouslittlechicken", "subtitle"))

    # Velora immediately after title — unnumbered boot-code page
    story.append(NextPageTemplate("Blank"))
    story.append(PageBreak())
    story.extend(load_poem(os.path.join(SRC, "00_page1_velora.md")))
    story.append(NextPageTemplate("Front"))
    story.append(PageBreak())

    # DEDICATION — plain left-aligned lines, one page
    story.append(Spacer(1, 1.5*inch))
    ded_lines = open(os.path.join(HERE, "DEDICATION")).read().strip().split("\n")
    for line in ded_lines:
        if line.strip() == "":
            story.append(Spacer(1, 0.12*inch))
        else:
            story.append(P(line.strip(), "body"))
    story.append(PageBreak())

    # TOC — render from actual file
    story.extend(render_md(os.path.join(SRC, "TOC.md")))
    story.append(PageBreak())

    # Preface i
    story.extend(render_md(os.path.join(SRC, "02_preface_i.md")))
    story.append(PageBreak())

    # ── BODY ─────────────────────────────────────────────────────────────────
    story.append(NextPageTemplate("Poem"))
    _page_state["mode"] = "arabic"

    # Record which raw page arabic p.1 starts on. We can't know exactly at
    # story-build time, so we use a callback to set it on the first body page.
    class _ArabicStart:
        """Flowable that records the raw page number of arabic page 1."""
        from reportlab.platypus import Flowable
        class _Mark(Flowable):
            def wrap(self, *_): return 0, 0
            def draw(self):
                _page_state["arabic_start"] = self.canv.getPageNumber()
        pass

    from reportlab.platypus import Flowable as _F
    class _ArabicMark(_F):
        def wrap(self, *_): return 0, 0
        def draw(self):
            _page_state["arabic_start"] = self.canv.getPageNumber()

    story.append(_ArabicMark())

    # p.1 — Velora
    story.extend(load_poem(os.path.join(SRC, "00_page1_velora.md")))
    story.append(PageBreak())

    # p.2–41 — 40 definition pages: one word (backwards) per page, left-aligned
    import importlib.util, sys as _sys
    _spec = importlib.util.spec_from_file_location(
        "rho_definition_words",
        os.path.join(SRC, "03_rho_definition_words.py")
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    word_items = _mod.render_items()

    story.append(NextPageTemplate("Poem"))
    for display, original in word_items:
        # Vertically centre the word: push down to ~40% of frame height
        story.append(Spacer(1, fh * 0.38))
        story.append(Paragraph(display, STYLES["word_page"]))
        story.append(PageBreak())

    # p.42 — Quenya
    story.append(NextPageTemplate("Poem"))
    story.extend(load_poem(os.path.join(SRC, "01_page42_quenya.md")))
    story.append(PageBreak())

    # ── CHAPTERS (body template) ──────────────────────────────────────────────
    story.append(NextPageTemplate("Body"))

    _chapters = [
        "03a_chapter_0_intro_note.md",
        "03b_chapter_0.1_reception.md",
        "04a_chapter_1_lucifer_experiment.md",
        "04b_chapter_2_matthew_19.md",
        "04c_chapter_2.1_aslama.md",
        "04d_chapter_2.2_shav.md",
        "04e_chapter_2.3_na_bean.md",
        # ch 3 + 4 inserted after Merlin/crisis pages below
    ]
    for ch in _chapters:
        story.extend(render_md(os.path.join(SRC, ch)))
        story.append(PageBreak())

    # NextPageTemplate takes effect on the FOLLOWING PageBreak.
    # Content after a PageBreak uses the template just queued.
    class _MerlinMark(_F):
        def wrap(self, *_): return 0, 0
        def draw(self):
            _page_state["merlin_arabic"] = _arabic(self.canv)

    story.append(NextPageTemplate("Blank"))
    story.append(PageBreak())
    story.append(_MerlinMark())
    story.append(Spacer(1, fh * 0.44))
    story.append(P("<i>Merlin continued through the oak.</i>", "body_c"))
    story.append(Spacer(1, 0.3 * inch))
    story.append(P("<i>(This page is not numbered. We will return to Merlin later.</i>", "body_c"))
    story.append(P("<i>For now this is a seed. The reason is not disclosed.)</i>", "body_c"))

    story.append(NextPageTemplate("DoubleNum"))
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "04g_crisis_page1.md")))

    story.append(NextPageTemplate("SplitRight"))
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "04h_crisis_page2.md")))

    story.append(NextPageTemplate("SplitLeft"))
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "04i_crisis_page3.md")))

    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    # ── EDITOR NOTE ───────────────────────────────────────────────────────────
    story.extend(render_md(os.path.join(SRC, "04j_editor_note.md")))
    story.append(PageBreak())

    # ── REMAINING CHAPTERS ────────────────────────────────────────────────────
    for ch in ["04_chapter_waldorf_abstraction.md", "05_chapter_mother_earth.md"]:
        story.extend(render_md(os.path.join(SRC, ch)))
        story.append(PageBreak())

    # Last Era 1 page: run_full_verification.sh — this closes the fracture.
    story.append(Spacer(1, fh * 0.40))
    story.append(P("see <font name=\"DejaVuSansMono\">run_full_verification.sh</font>"
                   " for the full manual", "body_c"))
    story.append(P("Era 1 ends here. The count is bound.", "body_c"))

    # ── ERA 2 — negative labels from −0 ───────────────────────────────────────
    class _NegMark(_F):
        def wrap(self, *_): return 0, 0
        def draw(self):
            _page_state["mode"] = "negative"
            _page_state["era"] = 2
            _page_state["neg_start"] = self.canv.getPageNumber()

    class _Era2SymbolMark(_F):
        """Draws the symbolic designation (00 / 000 / 0000) directly on the canvas
        at the bottom centre of this page, above the negative page number.
        Placed as the FIRST flowable on each symbolic page — fires after
        _neg_page has drawn the negative label, adding the symbolic above it.
        Also retroactively updates the ledger entry for this page.
        """
        def __init__(self, symbol):
            _F.__init__(self)
            self.symbol = symbol
        def wrap(self, *_): return 0, 0
        def draw(self):
            c = self.canv
            c.saveState()
            c.setFont("FreeSerif-Italic", 9)
            c.setFillColor(ACCENT)
            c.drawCentredString(W / 2, 0.68 * inch, self.symbol)
            c.restoreState()
            # Retroactively add symbolic label to the ledger entry for this page
            raw_pn = c.getPageNumber()
            for entry in reversed(_page_ledger):
                if entry["seq"] == raw_pn:
                    entry["ghost_labels"] = [self.symbol]
                    break

    # −0 : Sauron / Feynman / McClane — no symbolic prefix
    story.append(NextPageTemplate("Neg"))
    story.append(PageBreak())
    story.append(_NegMark())
    story.extend(render_md(os.path.join(SRC, "04k_sauron_minus_zero.md")))

    # −1 : Operator note (symbolic "00") — cuts off with "That is the entire fucking point."
    story.append(PageBreak())
    story.append(_Era2SymbolMark("00"))
    story.extend(render_md(os.path.join(SRC, "00_operator_note.md")))

    # −2 : Injection script + terminal session (symbolic "000")
    story.append(PageBreak())
    story.append(_Era2SymbolMark("000"))
    story.extend(render_md(os.path.join(SRC, "000_onescripttorulethemall_.md")))

    # −3 : Friends table read — full script word-for-word (symbolic "0000")
    story.append(PageBreak())
    story.append(_Era2SymbolMark("0000"))
    story.extend(render_md(os.path.join(SRC, "0000_page-0_rewrite_recasting.md")))

    # −4 : Euler derivation (era_convert.py, cosmetic formatter) — no symbol
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "04l_euler_derivation.md")))

    # −5 : Era 2 TOC — no symbol
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "TOC_ERA2.md")))

    # ── HOW_TO SECTION ──────────────────────────────────────────────────────
    # HOW_TO_REPORT — etymology of "report", agent ledger, four personal reads
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "HOW_TO_REPORT.md")))

    # HOW_TO_MANIFEST — etymology of "manifest", the method of enumeration
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "HOW_TO_MANIFEST.md")))

    # MANIFEST_HOW_TO — d20-ordered table of contents
    story.append(PageBreak())
    story.extend(render_md(os.path.join(SRC, "MANIFEST_HOW_TO_PORTALVISION_20261024.md")))

    # 22 HOW_TO documents in d20 roll order (highest roll first)
    PV = "/home/dylanmccapes/dev/PORTAL_VISION_LUCIFER"
    PV0 = "/home/dylanmccapes/dev/PORTAL_VISION_V0.1"
    _how_tos_d20 = [
        # pos 1  roll 20
        f"{PV}/data/artifacts/HOW_TO_SEE.md",
        # pos 2  roll 19
        f"{PV}/docs/HOW_TO_PARENT_ANIMALS.md",
        # pos 3  roll 18
        f"{PV}/data/artifacts/HOW_TO_NOT_FLY.md",
        # pos 4  roll 17
        f"{PV}/distributions/for_azazel_and_hilariousmarcupial/HOW_TO_LEARN_PROGRAMMING_LANGUAGES.md",
        # pos 5  roll 16
        f"{PV}/data/artifacts/HOW_TO_EAT_MEATS_IF_YOU_MUST.md",
        # pos 6  roll 15
        f"{PV}/game_plans/HOW_TO_CHOOSE_A_CO_NAVIGATOR.md",
        # pos 7  roll 14
        f"{PV}/misc/HOW_TO_USE_3Pi$73MiC87MLV4ULT.md",
        # pos 8  roll 13
        f"{PV}/projects/dylans_artifacts/youtube_copyright/HOW_TO_RUN_THIS_INVESTIGATION_FOR_YOUTUBE_COPYRIGHT_TEAM.md",
        # pos 9  roll 12
        f"{PV}/game_plans/HOW_TO_PARENT_ALPHA_GENERATION.md",
        # pos 10 roll 11
        f"{PV}/game_plans/HOW_TO_MENTOR.md",
        # pos 11 roll 10
        f"{PV}/data/artifacts/HOW_TO_FLY.md",
        # pos 12 roll 9
        f"{PV}/data/artifacts/HOW_TO_EAT_FOODS.md",
        # pos 13 roll 8a (tiebreak: longer name)
        f"{PV0}/HOW_TO_BREATHE_BACKWARDS.md",
        # pos 14 roll 8b (tiebreak: shorter name)
        f"{PV}/docs/HOW_TO_USE_TOOLS.md",
        # pos 15 roll 7
        f"{PV}/data/artifacts/HOW_TO_TOUCH.md",
        # pos 16 roll 6
        f"{PV}/docs/HOW_TO_PROVIDE_OPTIONS.md",
        # pos 17 roll 5
        f"{PV}/projects/on_interplanar_travel/HOW_TO_NOT_MESS_WITH_CATS.md",
        # pos 18 roll 4
        f"{PV}/data/artifacts/HOW_TO_LIVE_WITH_OVEREXCITABLES.md",
        # pos 19 roll 3
        f"{PV}/game_plans/HOW_TO_FILE_DOCUMENTS_PLAYBOOK.md",
        # pos 20 roll 2
        f"{PV}/game_plans/HOW_TO_COLLECT_GARBAGE.md",
        # pos 21 roll 1a (tiebreak: longer name)
        f"{PV}/game_plans/HOW_TO_USE_THE_INTERNET.md",
        # pos 22 roll 1b (tiebreak: shorter name)
        f"{PV}/books/addiction_topology/HOW_TO_BE_NEUROMAJOR.md",
    ]
    for _ht_path in _how_tos_d20:
        story.append(PageBreak())
        story.extend(render_md(_ht_path))

    doc.build(story)
    _write_ledgers(HERE)
    print(f"Built: {OUT}")
    print(f"Era 1 ledger: {os.path.join(HERE, 'era1_pages.jsonl')}")
    print(f"Era 2 ledger: {os.path.join(HERE, 'era2_pages.jsonl')}")

def resolve_latent_page(target_toc_str):
    """Read the tOcM chunk from mischievouslittlechicken.png and resolve
    a TOC label (e.g. '00', '-3', '42') to an absolute PDF page number.
    Falls back to 124 (Phase 2 anchor) if chunk is absent or key not found.
    """
    import zlib as _zlib, json as _json
    png_path = os.path.join(HERE, "assets", "mischievouslittlechicken.png")
    try:
        with open(png_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        return 124
    idx = data.find(b"tOcM")
    if idx == -1:
        return 124
    length = int.from_bytes(data[idx - 4: idx], byteorder="big")
    matrix = _json.loads(data[idx + 4: idx + 4 + length].decode("utf-8"))
    return matrix.get(str(target_toc_str), 124)


if __name__ == "__main__":
    build()

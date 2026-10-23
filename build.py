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

import sys, os, re
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVu for Greek + Latin (ΚΑΤΑ title line)
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
MARGIN_OUTER = 1.1 * inch
MARGIN_INNER = 1.25 * inch
MARGIN_TOP   = 1.0 * inch
MARGIN_BOT   = 1.0 * inch

# ── page number state ─────────────────────────────────────────────────────────
_page_state = {"mode": "roman", "arabic_start": None}

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
    else:
        start = _page_state.get("arabic_start") or pn
        return str(pn - start + 1)

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
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(ACCENT)
    pnum = page_number_str(canvas)
    canvas.drawCentredString(W / 2, 0.6 * inch, pnum)
    # Title page: image + link bottom-right, stele-style
    if canvas.getPageNumber() == 1:
        if os.path.exists(_INSCRIPTION_PATH):
            canvas.drawImage(_INSCRIPTION_PATH,
                             _IMG_X, _IMG_Y,
                             width=_INS_W, height=_INS_H,
                             preserveAspectRatio=True, mask='auto')
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(ACCENT)
        canvas.drawRightString(W - MARGIN_OUTER, _LINK_Y, _TITLE_PAGE_URL)
    canvas.restoreState()

def _body_page(canvas, doc):
    canvas.saveState()
    pn_raw = canvas.getPageNumber()
    start  = _page_state.get("arabic_start", 1)
    arabic = pn_raw - start + 1
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(ACCENT)
    if arabic > 0:
        canvas.drawCentredString(W / 2, 0.6 * inch, str(arabic))
    # running head (title only)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2, H - 0.6 * inch, "REALITY_USER_MANUAL")
    canvas.restoreState()

def _blank_page(canvas, doc):
    """Intentionally blank — no number, no head."""
    pass

def _double_num_page(canvas, doc):
    """Carries two page numbers: the ghost (unnumbered Merlin page) and real."""
    canvas.saveState()
    pn_raw = canvas.getPageNumber()
    start  = _page_state.get("arabic_start", 1)
    arabic = pn_raw - start + 1
    ghost  = arabic - 1  # the page that wasn't numbered
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2 - 0.3 * inch, 0.6 * inch, str(ghost))
    canvas.drawCentredString(W / 2 + 0.3 * inch, 0.6 * inch, str(arabic))
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(W / 2, H - 0.6 * inch, "REALITY_USER_MANUAL")
    canvas.restoreState()

def _split_right_page(canvas, doc):
    """Crisis page 2: normal number centre + ghost at far bottom right."""
    canvas.saveState()
    pn_raw = canvas.getPageNumber()
    start  = _page_state.get("arabic_start", 1)
    arabic = pn_raw - start + 1
    ghost  = arabic - 2  # the Merlin ghost, two pages back
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawCentredString(W / 2, 0.6 * inch, str(arabic))
    canvas.drawRightString(W - MARGIN_OUTER, 0.6 * inch, str(ghost))
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(W / 2, H - 0.6 * inch, "REALITY_USER_MANUAL")
    canvas.restoreState()

def _split_left_page(canvas, doc):
    """Crisis page 3: ghost at far bottom left + normal number centre."""
    canvas.saveState()
    pn_raw = canvas.getPageNumber()
    start  = _page_state.get("arabic_start", 1)
    arabic = pn_raw - start + 1
    ghost  = arabic - 3  # the Merlin ghost, three pages back
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(ACCENT)
    canvas.drawString(MARGIN_INNER, 0.6 * inch, str(ghost))
    canvas.drawCentredString(W / 2, 0.6 * inch, str(arabic))
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(W / 2, H - 0.6 * inch, "REALITY_USER_MANUAL")
    canvas.restoreState()

def _poem_page(canvas, doc):
    """Poem pages: page number only, no running head."""
    canvas.saveState()
    pn_raw = canvas.getPageNumber()
    start  = _page_state.get("arabic_start", 1)
    arabic = pn_raw - start + 1
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(ACCENT)
    if arabic > 0:
        canvas.drawCentredString(W / 2, 0.6 * inch, str(arabic))
    canvas.restoreState()

# ── styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, parent="Normal", **kw):
    kw.setdefault("textColor", INK)
    return ParagraphStyle(name, parent=base[parent], **kw)

STYLES = {
    "word_page": S("word_page","Normal", fontName="Helvetica-Bold", fontSize=48,
                  leading=56, alignment=TA_LEFT, textColor=INK,
                  spaceBefore=0, spaceAfter=0),

    "poem":     S("poem",   "Normal", fontName="Times-Italic",  fontSize=11,
                  leading=18, alignment=TA_LEFT,
                  leftIndent=1.5*inch, spaceAfter=0),

    "poem_div": S("poem_div","Normal", fontName="Helvetica",    fontSize=9,
                  leading=14, alignment=TA_CENTER, textColor=ACCENT,
                  spaceBefore=14, spaceAfter=14),

    "title":    S("title",  "Normal", fontName="Helvetica-Bold", fontSize=28,
                  leading=34, alignment=TA_CENTER, spaceBefore=0,
                  spaceAfter=0.3*inch),

    "subtitle": S("subtitle","Normal", fontName="DejaVuBold",   fontSize=13,
                  leading=18, alignment=TA_CENTER, textColor=ACCENT,
                  spaceAfter=0.5*inch),

    "ded":      S("ded",    "Normal", fontName="Times-Italic",  fontSize=13,
                  leading=22, alignment=TA_CENTER, spaceBefore=1.5*inch,
                  spaceAfter=0.25*inch),

    "ded_plain":S("ded_plain","Normal",fontName="Times-Roman",  fontSize=11,
                  leading=18, alignment=TA_CENTER, spaceAfter=0.15*inch),

    "ded_sig":  S("ded_sig","Normal", fontName="Times-Italic",  fontSize=11,
                  leading=18, alignment=TA_RIGHT,  spaceAfter=0,
                  rightIndent=1.5*inch, spaceBefore=0.4*inch),

    "h1":       S("h1",     "Normal", fontName="Helvetica-Bold", fontSize=16,
                  leading=22, spaceBefore=0.4*inch, spaceAfter=0.15*inch),

    "h2":       S("h2",     "Normal", fontName="Helvetica-Bold", fontSize=12,
                  leading=18, spaceBefore=0.3*inch, spaceAfter=0.1*inch),

    "body":     S("body",   "Normal", fontName="Times-Roman",   fontSize=11,
                  leading=17, alignment=TA_JUSTIFY, spaceAfter=0.1*inch),

    "body_c":   S("body_c", "Normal", fontName="Times-Roman",   fontSize=11,
                  leading=17, alignment=TA_CENTER, spaceAfter=0.1*inch),

    "meta":     S("meta",   "Normal", fontName="Helvetica",     fontSize=9,
                  leading=13, textColor=ACCENT, spaceAfter=0.05*inch),

    "toc_h":    S("toc_h",  "Normal", fontName="Helvetica-Bold", fontSize=14,
                  leading=20, spaceBefore=0.5*inch, spaceAfter=0.3*inch,
                  alignment=TA_CENTER),

    "toc_empty":S("toc_empty","Normal",fontName="Times-Italic", fontSize=11,
                  leading=17, alignment=TA_CENTER, textColor=ACCENT,
                  spaceBefore=0.5*inch),

    "code":     S("code",   "Normal", fontName="Courier",       fontSize=8,
                  leading=11, leftIndent=0.5*inch, spaceBefore=6,
                  spaceAfter=6, alignment=TA_LEFT),
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
                    '<font name="Courier">' + cl.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') + '</font>',
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
            ('FONTNAME',  (0,0), (-1,0), 'Helvetica-Bold'),
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
    t = re.sub(r'`(.+?)`',       r'<font name="Courier">\1</font>', t)
    return t

# ── document assembly ─────────────────────────────────────────────────────────
HERE   = os.path.dirname(os.path.abspath(__file__))
SRC    = os.path.join(HERE, "src")
OUT    = os.path.join(HERE, "REALITY_USER_MANUAL.pdf")

def build():
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

    # ── MERLIN SEED — unnumbered page (Blank: no number drawn) ───────────────
    story.append(NextPageTemplate("Blank"))
    story.append(Spacer(1, fh * 0.44))
    story.append(P("<i>Merlin continued through the oak.</i>", "body_c"))
    story.append(Spacer(1, 0.3 * inch))
    story.append(P("<i>(This page is not numbered. We will return to Merlin later.</i>", "body_c"))
    story.append(P("<i>For now this is a seed. The reason is not disclosed.)</i>", "body_c"))
    story.append(PageBreak())

    # ── CRISIS PAGE 1 — DoubleNum ─────────────────────────────────────────────
    story.append(NextPageTemplate("DoubleNum"))
    story.extend(render_md(os.path.join(SRC, "04g_crisis_page1.md")))
    story.append(PageBreak())

    # ── CRISIS PAGE 2 — SplitRight ────────────────────────────────────────────
    story.append(NextPageTemplate("SplitRight"))
    story.extend(render_md(os.path.join(SRC, "04h_crisis_page2.md")))
    story.append(PageBreak())

    # ── CRISIS PAGE 3 — SplitLeft ─────────────────────────────────────────────
    story.append(NextPageTemplate("SplitLeft"))
    story.extend(render_md(os.path.join(SRC, "04i_crisis_page3.md")))
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    # ── REMAINING CHAPTERS ────────────────────────────────────────────────────
    for ch in ["04_chapter_waldorf_abstraction.md", "05_chapter_mother_earth.md"]:
        story.extend(render_md(os.path.join(SRC, ch)))
        story.append(PageBreak())

    # Last page: run_full_verification.sh reference
    story.append(Spacer(1, fh * 0.40))
    story.append(P("see <font name=\"Courier\">run_full_verification.sh</font>"
                   " for the full manual", "body_c"))

    doc.build(story)
    print(f"Built: {OUT}")

if __name__ == "__main__":
    build()

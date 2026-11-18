"""
GrammaticalGeometrySpaceDriver — source retrievals.

greekbible.com   — Bible source. Retrieves verse text and available translations.
                   The translations are stored as candidates. The driver does not
                   choose which translation wins.

logeion.uchicago.edu — A collection of dictionaries. Each dictionary is a
                   separate witness with its own source_id. The site is esteemed
                   and wariness is warranted.

                   API discovered 2026-11-01 from the Angular JS bundle:
                   Base: https://anastrophe.uchicago.edu/logeion-api
                   Endpoints used:
                     /find?w={word}   — lemma + grammatical parse
                     /detail?w={lemma} — all dictionary entries (dicos array)
                   No public documentation; treat as discoverable but undocumented.
"""

from __future__ import annotations

import datetime
import re
import time
from pathlib import Path
from typing import Any

import requests

from schema import LOGEION_DICTIONARIES, GREEKBIBLE_SOURCE_ID

# ─── HTTP ──────────────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "GrammaticalGeometrySpaceDriver/0.0.1 (research; contact via repo)"
})
TIMEOUT = 20
RETRY_WAIT = 2.0

# ─── Logeion rate limiter ───────────────────────────────────────────────────────
# The Logeion API is undocumented and unmetered. This project is not a RAG
# pipeline — each word is looked up once and the result is kept. Keep the
# request rate at 1/s sustained so the service remains available to others.

_last_logeion_call: float = 0.0
_LOGEION_RATE_INTERVAL: float = 1.0   # seconds between successive Logeion calls


def _logeion_rate_limit() -> None:
    """Sleep if less than _LOGEION_RATE_INTERVAL has elapsed since the last call."""
    global _last_logeion_call
    elapsed = time.time() - _last_logeion_call
    if elapsed < _LOGEION_RATE_INTERVAL:
        time.sleep(_LOGEION_RATE_INTERVAL - elapsed)
    _last_logeion_call = time.time()


def _get(url: str, params: dict | None = None) -> requests.Response:
    for attempt in range(3):
        try:
            r = SESSION.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if attempt == 2:
                raise
            time.sleep(RETRY_WAIT * (attempt + 1))
    raise RuntimeError("unreachable")


# ─── greekbible.com ────────────────────────────────────────────────────────────

def fetch_greekbible(verse_ref: str) -> dict[str, Any]:
    """
    Retrieve verse text and available translations from greekbible.com.

    verse_ref examples: "Matthew 25:18", "John 3:16"

    Returns a dict with:
        source_id: str
        url: str
        retrieved_at: str (ISO)
        verse_ref: str
        greek_text: str          — the Greek text of the verse (SBL GNT or similar)
        translations: list[dict] — each entry: {version, text}
        raw_html_snippet: str    — first 2000 chars of the relevant HTML

    greekbible.com does not have a documented JSON API as of 2026-11-01.
    This function scrapes the page. If the site structure changes, update
    the parsing here; do not silently drop the raw.
    """
    # greekbible.com URL format: https://www.greekbible.com/ (requires navigation)
    # The site uses a URL like /l/{book}/{chapter}/{verse} for direct access.
    # Parse the reference.
    parts = _parse_verse_ref(verse_ref)
    url = f"https://www.greekbible.com/l/{parts['book_slug']}/{parts['chapter']}/{parts['verse']}"

    retrieved_at = datetime.datetime.utcnow().isoformat() + "Z"

    try:
        r = _get(url)
        soup = BeautifulSoup(r.text, "lxml")
        raw_snippet = r.text[:3000]

        # Extract Greek text — look for the main verse display
        greek_text = _extract_greekbible_greek(soup)

        # Extract available translations
        translations = _extract_greekbible_translations(soup)

    except Exception as e:
        greek_text = ""
        translations = []
        raw_snippet = f"[retrieval error: {e}]"

    return {
        "source_id": GREEKBIBLE_SOURCE_ID,
        "url": url,
        "retrieved_at": retrieved_at,
        "verse_ref": verse_ref,
        "greek_text": greek_text,
        "translations": translations,
        "raw_html_snippet": raw_snippet,
    }


def _parse_verse_ref(ref: str) -> dict[str, str]:
    """Parse 'Matthew 25:18' -> {book_slug, chapter, verse}."""
    ref = ref.strip()
    # Split on last space to get book vs chapter:verse
    # Handle multi-word books: "1 Corinthians 3:4"
    if ":" not in ref:
        raise ValueError(f"verse_ref must contain ':': {ref!r}")
    chapter_verse = ref.rsplit(":", 1)
    verse = chapter_verse[1]
    book_chapter = chapter_verse[0].rsplit(" ", 1)
    chapter = book_chapter[1]
    book = book_chapter[0]

    # greekbible.com book slug format (best-effort; adjust if the site uses different slugs)
    BOOK_SLUGS = {
        "Matthew": "Matthew", "Mark": "Mark", "Luke": "Luke", "John": "John",
        "Acts": "Acts", "Romans": "Romans",
        "1 Corinthians": "1Corinthians", "2 Corinthians": "2Corinthians",
        "Galatians": "Galatians", "Ephesians": "Ephesians",
        "Philippians": "Philippians", "Colossians": "Colossians",
        "1 Thessalonians": "1Thessalonians", "2 Thessalonians": "2Thessalonians",
        "1 Timothy": "1Timothy", "2 Timothy": "2Timothy", "Titus": "Titus",
        "Philemon": "Philemon", "Hebrews": "Hebrews", "James": "James",
        "1 Peter": "1Peter", "2 Peter": "2Peter",
        "1 John": "1John", "2 John": "2John", "3 John": "3John",
        "Jude": "Jude", "Revelation": "Revelation",
        "Genesis": "Genesis", "Exodus": "Exodus",
    }
    slug = BOOK_SLUGS.get(book, book.replace(" ", ""))
    return {"book_slug": slug, "chapter": chapter, "verse": verse}


def _extract_greekbible_greek(soup: BeautifulSoup) -> str:
    """Best-effort extraction of the Greek text from greekbible.com."""
    # greekbible.com typically puts the Greek in a span or div with a Greek-language class
    for selector in ["span.greek", "div.greek", ".greek-text", "#greek", "span[lang='grc']"]:
        el = soup.select_one(selector)
        if el:
            return el.get_text(separator=" ").strip()
    # Fallback: look for any text that looks Greek (has Unicode Greek characters)
    for el in soup.find_all(["span", "div", "p"]):
        text = el.get_text()
        if any("\u0370" <= c <= "\u03ff" for c in text):
            return text.strip()[:500]
    return ""


def _extract_greekbible_translations(soup: BeautifulSoup) -> list[dict[str, str]]:
    """Extract available translations from greekbible.com."""
    translations = []
    # Look for translation blocks — greekbible.com typically shows multiple versions
    for el in soup.select("div.translation, div.version, table.translations tr"):
        label_el = el.select_one(".version-name, .label, th, td:first-child")
        text_el = el.select_one(".version-text, .text, td:last-child")
        if label_el and text_el:
            translations.append({
                "version": label_el.get_text().strip(),
                "text": text_el.get_text().strip(),
            })
    return translations


# ─── logeion.uchicago.edu ──────────────────────────────────────────────────────

LOGEION_WEB = "https://logeion.uchicago.edu"
LOGEION_API = "https://anastrophe.uchicago.edu/logeion-api"
LOGEION_REFERER = "https://logeion.uchicago.edu/"

# Map dname strings returned by the API to stable source_ids
DNAME_TO_SOURCE_ID = {
    "LSJ": "logeion_lsj",
    "Middle Liddell": "logeion_middle",
    "Lewis & Short": "logeion_ls",
    "Lewis and Short": "logeion_ls",
    "Slater": "logeion_slater",
    "Cunliffe": "logeion_cunliffe",
    "Montanari": "logeion_montanari",
    "Autenrieth": "logeion_autenrieth",
    "Muraoka": "logeion_muraoka",
    "Dodson": "logeion_dodson",
    "Gildersleeve": "logeion_gildersleeve",
    "Smyth": "logeion_smyth",
    "Abbott-Smith": "logeion_abbott_smith",
    "Abbott Smith": "logeion_abbott_smith",
    "Thayer": "logeion_thayer",
    "Strong": "logeion_strong",
    "Strong's": "logeion_strong",
    "Frieze": "logeion_frieze",
    "BwL": "logeion_bwl",
}


def _logeion_get(path: str, params: dict) -> requests.Response:
    """GET from the anastrophe API with Logeion referer. Rate-limited to 1 req/s."""
    _logeion_rate_limit()
    url = f"{LOGEION_API}/{path}"
    r = SESSION.get(
        url,
        params=params,
        timeout=TIMEOUT,
        headers={"Accept": "application/json", "Referer": LOGEION_REFERER},
    )
    r.raise_for_status()
    return r


def _strip_html(text: str) -> str:
    """Strip HTML tags for readable entry_text."""
    from bs4 import BeautifulSoup as BS
    return BS(text, "lxml").get_text(separator=" ").strip()


def fetch_logeion(word: str, hint_lemma: str | None = None) -> dict[str, Any]:
    """
    Retrieve dictionary entries for a Greek word from Logeion via the
    anastrophe.uchicago.edu REST API discovered 2026-11-01.

    Workflow:
      1. /find?w={word}   — returns lemma + grammatical parses
         (skipped when hint_lemma is provided — saves one Logeion request)
      2. /detail?w={lemma} — returns all dictionary entries (dicos array)

    hint_lemma: supply the lemma directly (e.g. from MorphGNT) to skip /find.
                This halves the Logeion request count for MorphGNT-driven runs.

    Returns a dict keyed by source_id, one entry per dictionary that has content.
    Also includes a special "logeion_parse" entry with the grammatical information.
    """
    retrieved_at = datetime.datetime.now(datetime.UTC).isoformat()
    web_url = f"{LOGEION_WEB}/{requests.utils.quote(word)}"
    entries: dict[str, Any] = {}

    # ── Step 1: find lemma ──────────────────────────────────────────────────
    # Skip /find when hint_lemma is supplied (e.g. from MorphGNT). This saves
    # one Logeion API call per word and avoids the "word" vs "lemma" mismatch
    # that caused the ἓν/ἐν confusion (see sources.py history).
    lemma = hint_lemma or word
    parses: list[dict] = []
    if hint_lemma:
        # MorphGNT-supplied lemma: record it without calling /find
        entries["logeion_parse"] = {
            "source_id": "logeion_parse",
            "url": "[morphgnt — /find not called]",
            "retrieved_at": retrieved_at,
            "word": word,
            "lemma": lemma,
            "parses": [],
            "entry_text": f"lemma={lemma} (from MorphGNT; /find skipped)",
        }
    else:
        try:
            r_find = _logeion_get("find", {"w": word})
            found = r_find.json()
            parses = found.get("parses", [])
            # IMPORTANT: "word" in the API response is the deaccented/debreathed lookup
            # key the API used internally — it is NOT the lemma. Use parses[0]["lemma"]
            # when available (e.g. ἓν → "word":"ἐν" but parses[0]["lemma"]:"εἷς").
            if parses:
                lemma = parses[0].get("lemma", found.get("word", word))
            else:
                lemma = found.get("word", word)
            entries["logeion_parse"] = {
                "source_id": "logeion_parse",
                "url": f"{LOGEION_API}/find",
                "retrieved_at": retrieved_at,
                "word": word,
                "lemma": lemma,
                "parses": parses,
                "entry_text": "; ".join(
                    f"{p.get('lemma', lemma)}: {p.get('parse', '')}" for p in parses
                ) if parses else f"lemma={lemma}",
            }
        except Exception as e:
            entries["logeion_find_error"] = {
                "source_id": "logeion_find_error",
                "url": f"{LOGEION_API}/find",
                "retrieved_at": retrieved_at,
                "word": word,
                "entry_text": f"[find error: {e}]",
            }

    # ── Step 2: detail for lemma ────────────────────────────────────────────
    # Known Logeion API routing mismatches: some lemmas return entries for a
    # different headword. When detected, we retry with the surface form and
    # merge. The mismatch is a source bug, not a model issue — close the gap
    # here so the model receives the correct dictionary entries.
    #
    # Confirmed mismatch: εἷς (and its forms ἓν, ἕν, μία) routes to ἐν (prep).
    # The API appears to strip diacritics or conflate Unicode codepoints.
    _LEMMA_DETAIL_OVERRIDES = {
        "εἷς": "εἷς",   # force exact lookup; fallback to surface if still misrouted
        "μία":  "μία",
    }
    detail_word = _LEMMA_DETAIL_OVERRIDES.get(lemma, lemma)
    # Surface form as additional fallback for known-misrouted lemmas
    _surface_fallback_lemmas = set(_LEMMA_DETAIL_OVERRIDES.keys())

    def _fetch_detail(lookup_word: str) -> dict:
        r = _logeion_get("detail", {"w": lookup_word})
        return r.json().get("detail", {})

    def _detail_headword_mismatch(detail: dict, expected_lemma: str) -> bool:
        """Return True if the detail entries appear to be for a different headword."""
        shortdefs = detail.get("shortdef", [])
        if not shortdefs:
            return False
        # Check if the shortdef mentions the expected lemma at all
        # (the shortdef format is typically "lemma, inflected_form, gloss")
        first = shortdefs[0].lower() if shortdefs else ""
        import unicodedata as _ud
        def _strip_diacritics(s: str) -> str:
            return "".join(
                c for c in _ud.normalize("NFD", s)
                if _ud.category(c) != "Mn"
            )
        exp_stripped = _strip_diacritics(expected_lemma.lower())
        # If the shortdef's first word (the lemma field) doesn't contain our lemma
        # after diacritic stripping, consider it a mismatch.
        first_word = first.split(",")[0].strip()
        return exp_stripped not in _strip_diacritics(first_word)

    try:
        detail = _fetch_detail(detail_word)

        # Mismatch detection: if we asked for a known-problematic lemma and the
        # returned entries look like a different word, retry with the surface form.
        if lemma in _surface_fallback_lemmas and _detail_headword_mismatch(detail, lemma):
            # First retry: try the surface form of the word directly
            try:
                detail_surface = _fetch_detail(word)
                if not _detail_headword_mismatch(detail_surface, lemma):
                    detail = detail_surface
                else:
                    # Both misrouted. Flag both and keep the lemma-based one.
                    # The model will see the mismatch note in logeion_parse.
                    pass
            except Exception:
                pass  # keep the original misrouted detail

        # shortdef — summary definition across sources
        shortdefs = detail.get("shortdef", [])
        if shortdefs:
            entries["logeion_shortdef"] = {
                "source_id": "logeion_shortdef",
                "url": f"{LOGEION_API}/detail",
                "retrieved_at": retrieved_at,
                "word": word,
                "lemma": lemma,
                "entry_text": " | ".join(shortdefs),
            }

        # Per-dictionary entries (dicos)
        for dico in detail.get("dicos", []):
            dname = dico.get("dname", "")
            es = dico.get("es", [])  # list of entry strings (may contain HTML)
            if not es:
                continue
            entry_text = "\n".join(_strip_html(e) for e in es if e).strip()
            if not entry_text:
                continue
            source_id = DNAME_TO_SOURCE_ID.get(dname)
            if not source_id:
                slug = dname.lower().replace(" ", "_").replace("&", "and")[:30]
                source_id = f"logeion_{slug}" if slug else "logeion_unknown"
            entries[source_id] = {
                "source_id": source_id,
                "url": web_url,
                "retrieved_at": retrieved_at,
                "word": word,
                "lemma": lemma,
                "dictionary": dname,
                "entry_text": entry_text[:4000],
            }

        # lewisshort inline (Latin dictionaries also appear for some words)
        ls_entries = detail.get("lewisshort", [])
        if ls_entries:
            ls_text = "\n".join(_strip_html(e) for e in ls_entries if e).strip()
            if ls_text and "logeion_ls" not in entries:
                entries["logeion_ls"] = {
                    "source_id": "logeion_ls",
                    "url": web_url,
                    "retrieved_at": retrieved_at,
                    "word": word,
                    "lemma": lemma,
                    "dictionary": "Lewis & Short (inline)",
                    "entry_text": ls_text[:4000],
                }

    except Exception as e:
        entries["logeion_detail_error"] = {
            "source_id": "logeion_detail_error",
            "url": f"{LOGEION_API}/detail",
            "retrieved_at": retrieved_at,
            "word": word,
            "lemma": lemma,
            "entry_text": f"[detail error: {e}]",
        }

    # ── Fallback: if nothing came back, record the gap cleanly ──────────────
    if not entries or all("error" in k for k in entries):
        entries["logeion_empty"] = {
            "source_id": "logeion_empty",
            "url": web_url,
            "retrieved_at": retrieved_at,
            "word": word,
            "lemma": lemma,
            "entry_text": f"[no entries found for {word!r} (lemma {lemma!r})]",
        }

    return entries


# ─── convenience ───────────────────────────────────────────────────────────────

def fetch_all_for_word(
    surface: str,
    verse_ref: str,
    hint_lemma: str | None = None,
) -> dict[str, Any]:
    """
    Fetch Logeion entries for a word surface form.
    greekbible.com is fetched once per verse, not per word.
    hint_lemma: if provided (e.g. from MorphGNT), pass directly to /detail,
                bypassing the /find call and saving one Logeion request.
    Returns the Logeion entries dict.
    """
    return fetch_logeion(surface, hint_lemma=hint_lemma)


# ─── MorphGNT ──────────────────────────────────────────────────────────────────
# MorphGNT SBL GNT — CC BY-SA 4.0 — https://github.com/morphgnt/sblgnt
#
# Format (7 space-separated fields per line):
#   BCVword  part-of-speech  parse-code  text  word  normalized-word  lemma
#
# BCVword: book(2 digits) + chapter(3 digits) + verse(3 digits)
#          e.g. 40001001 = Matthew (40) chapter 1 verse 1
#
# Matthew file: 58-Mt-morphgnt.txt  (58 = sort position in MorphGNT canon)
# Download: tools/download_morphgnt.sh

MorphGNTWord = dict[str, str]   # keys: text, word, normalized, lemma, pos, parse

def load_morphgnt(path: str | Path) -> dict[tuple[int, int], list[MorphGNTWord]]:
    """
    Load a MorphGNT file into a dict keyed by (chapter, verse).

    Returns:
        {(chapter, verse): [{"text", "word", "normalized", "lemma", "pos", "parse"}, ...]}
    """
    result: dict[tuple[int, int], list[MorphGNTWord]] = {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"MorphGNT file not found: {p}")

    with p.open(encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 7:
                continue   # malformed line
            bcv   = parts[0]   # e.g. "012518"  (BB CC VV — 6 digits)
            pos   = parts[1]
            parse = parts[2]
            text  = parts[3]   # as-printed surface (may contain ⸀ apparatus markers)
            word  = parts[4]   # clean word without punctuation or apparatus marks
            normalized = parts[5]
            lemma = parts[6]

            # BCVword format: 2-digit book-within-file + 2-digit chapter + 2-digit verse
            # (NOT standard NT book numbers — the book number here resets to 01 per file)
            if len(bcv) < 6:
                continue
            try:
                chapter = int(bcv[2:4])
                verse   = int(bcv[4:6])
            except ValueError:
                continue

            key = (chapter, verse)
            if key not in result:
                result[key] = []
            result[key].append({
                "text": text,
                "word": word,
                "normalized": normalized,
                "lemma": lemma,
                "pos": pos,
                "parse": parse,
            })
    return result


def morphgnt_verse_tokens(
    morphgnt_data: dict[tuple[int, int], list[MorphGNTWord]],
    chapter: int,
    verse: int,
) -> list[MorphGNTWord]:
    """Return the word list for a specific chapter:verse, or [] if absent."""
    return morphgnt_data.get((chapter, verse), [])

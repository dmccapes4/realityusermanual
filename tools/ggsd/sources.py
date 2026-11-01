"""
GrammaticalGeometrySpaceDriver — source retrievals.

greekbible.com   — Bible source. Retrieves verse text and available translations.
                   The translations are stored as candidates. The driver does not
                   choose which translation wins.

logeion.uchicago.edu — A collection of dictionaries. Each dictionary is a
                   separate witness with its own source_id. The site is esteemed
                   and wariness is warranted. As of 2026-11-01, no public API
                   was confirmed; retrieval uses the web interface. If an API
                   is found, the retrieval function is updated here and nowhere else.
"""

from __future__ import annotations

import datetime
import time
from typing import Any

import requests
from bs4 import BeautifulSoup

from schema import LOGEION_DICTIONARIES, GREEKBIBLE_SOURCE_ID

# ─── HTTP ──────────────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "GrammaticalGeometrySpaceDriver/0.0.1 (research; contact via repo)"
})
TIMEOUT = 20
RETRY_WAIT = 2.0


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

LOGEION_BASE = "https://logeion.uchicago.edu"


def fetch_logeion(word: str) -> dict[str, Any]:
    """
    Retrieve dictionary entries for a Greek word from Logeion.

    Returns a dict keyed by source_id (one per dictionary found):
        {
          "logeion_lsj": {
              "source_id": ...,
              "url": ...,
              "retrieved_at": ...,
              "word": ...,
              "entry_text": ...,
              "raw_html_snippet": ...,
          },
          ...
        }

    Logeion aggregates multiple dictionaries on one page.
    The page is parsed to separate each dictionary's entry.

    NOTE: As of 2026-11-01, no public JSON API was confirmed for Logeion.
    If an API exists, replace _fetch_logeion_web with _fetch_logeion_api here.
    The raw retrieval is always stored so the parse can be re-run.
    """
    url = f"{LOGEION_BASE}/{requests.utils.quote(word)}"
    retrieved_at = datetime.datetime.utcnow().isoformat() + "Z"

    try:
        r = _get(url)
        soup = BeautifulSoup(r.text, "lxml")
        raw_snippet = r.text[:5000]
        entries = _parse_logeion_entries(soup, word, retrieved_at)
    except Exception as e:
        raw_snippet = f"[retrieval error: {e}]"
        entries = {
            "logeion_error": {
                "source_id": "logeion_error",
                "url": url,
                "retrieved_at": retrieved_at,
                "word": word,
                "entry_text": f"[error: {e}]",
                "raw_html_snippet": raw_snippet,
            }
        }

    return entries


def _parse_logeion_entries(
    soup: BeautifulSoup, word: str, retrieved_at: str
) -> dict[str, Any]:
    """
    Parse Logeion's multi-dictionary page into per-dictionary entries.

    Logeion renders each dictionary in a labelled section. The labels typically
    match known dictionary names (LSJ, Middle Liddell, etc.).
    """
    # Map display labels to source_ids
    LABEL_TO_SOURCE = {
        "lsj": "logeion_lsj",
        "liddell-scott-jones": "logeion_lsj",
        "liddell scott jones": "logeion_lsj",
        "middle liddell": "logeion_middle",
        "middle": "logeion_middle",
        "lewis & short": "logeion_ls",
        "lewis and short": "logeion_ls",
        "slater": "logeion_slater",
        "cunliffe": "logeion_cunliffe",
        "montanari": "logeion_montanari",
        "autenrieth": "logeion_autenrieth",
        "muraoka": "logeion_muraoka",
        "dodson": "logeion_dodson",
        "gildersleeve": "logeion_gildersleeve",
        "smyth": "logeion_smyth",
        "abbott-smith": "logeion_abbott_smith",
        "abbott smith": "logeion_abbott_smith",
        "thayer": "logeion_thayer",
        "strong": "logeion_strong",
        "strong's": "logeion_strong",
    }

    entries = {}
    url = f"{LOGEION_BASE}/{requests.utils.quote(word)}"

    # Logeion typically renders dictionaries in labelled divs or sections
    for section in soup.select("div.dictionary-entry, section.dict, div.dict-section, .lexicon"):
        # Try to find the dictionary label
        label_el = section.select_one("h2, h3, h4, .dict-name, .lexicon-name, .source-name")
        label = label_el.get_text().strip().lower() if label_el else ""

        source_id = None
        for key, sid in LABEL_TO_SOURCE.items():
            if key in label:
                source_id = sid
                break

        if not source_id:
            # Use label as-is if not recognized, prefixed with logeion_
            source_id = "logeion_" + label.replace(" ", "_")[:30] if label else "logeion_unknown"

        entry_text = section.get_text(separator="\n").strip()
        if not entry_text:
            continue

        entries[source_id] = {
            "source_id": source_id,
            "url": url,
            "retrieved_at": retrieved_at,
            "word": word,
            "entry_text": entry_text[:4000],
            "raw_html_snippet": str(section)[:2000],
        }

    # If no sections found, store the whole page as a single entry
    if not entries:
        entries["logeion_raw"] = {
            "source_id": "logeion_raw",
            "url": url,
            "retrieved_at": retrieved_at,
            "word": word,
            "entry_text": soup.get_text(separator="\n").strip()[:4000],
            "raw_html_snippet": "[full page stored as single entry — section parse found nothing]",
        }

    return entries


# ─── convenience ───────────────────────────────────────────────────────────────

def fetch_all_for_word(surface: str, verse_ref: str) -> dict[str, Any]:
    """
    Fetch Logeion entries for a word surface form.
    greekbible.com is fetched once per verse, not per word.
    Returns the Logeion entries dict.
    """
    return fetch_logeion(surface)

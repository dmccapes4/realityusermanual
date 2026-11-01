"""
GrammaticalGeometrySpaceDriver — primitive schema and validation.

A primitive is one JSON object for one word in a verse.
The model may PROPOSE properties. It may not eliminate.
Elimination requires a consented rule (consent field set by the operator).
"""

from __future__ import annotations

import datetime
from typing import Any

# ─── field keys ────────────────────────────────────────────────────────────────

PRIMITIVE_FIELDS = [
    "meta_data",
    "verse",
    "word",
    "description",
    "grammatical_rules",
    "lexical_rules",
    "semantic_rules",
    "translations",
    "possible_interpretations",
    "edges",
    "source_retrievals",
    "source_agreements",
    "eliminations",
]

# ─── source registry ───────────────────────────────────────────────────────────

# Known dictionary ids within Logeion. Each is a separate witness.
# An agent may not add to this list. The operator adds dictionaries here.
LOGEION_DICTIONARIES = [
    "logeion_lsj",         # Liddell–Scott–Jones, full
    "logeion_middle",      # Middle Liddell
    "logeion_ls",          # Lewis & Short (Latin; present on logeion for cross-reference)
    "logeion_slater",      # Slater (Pindar)
    "logeion_cunliffe",    # Cunliffe (Homer)
    "logeion_montanari",   # Montanari (GE)
    "logeion_autenrieth",  # Autenrieth (Homeric)
    "logeion_muraoka",     # Muraoka (LXX)
    "logeion_dodson",      # Dodson (NT Greek)
    "logeion_gildersleeve", # Gildersleeve (syntax)
    "logeion_smyth",       # Smyth (syntax)
    "logeion_abbott_smith", # Abbott-Smith (NT)
    "logeion_thayer",      # Thayer (NT)
    "logeion_strong",      # Strong's (NT)
]

GREEKBIBLE_SOURCE_ID = "greekbible_com"


# ─── primitive builder ─────────────────────────────────────────────────────────

def empty_primitive(verse_ref: str, surface: str, model_id: str) -> dict[str, Any]:
    """Return an empty primitive for a word."""
    return {
        "meta_data": {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "model_id": model_id,
            "sources": [],
        },
        "verse": verse_ref,
        "word": {
            "surface": surface,
            "letters": list(surface),
        },
        "description": "",
        "grammatical_rules": [],
        "lexical_rules": [],
        "semantic_rules": [],
        "translations": [],
        "possible_interpretations": [],
        "edges": [],
        "source_retrievals": {},   # source_id -> {retrieved_at, url, raw}
        "source_agreements": [],   # see AgreementRecord below
        "eliminations": [],        # see EliminationRecord below
    }


# ─── rule schema ───────────────────────────────────────────────────────────────

def make_rule(
    category: str,          # "grammatical" | "lexical" | "semantic"
    value: str,             # the property asserted
    source_id: str,         # which source stated this
    quotation: str,         # verbatim from the source
    status: str = "proposed",  # "proposed" | "consented" (operator sets)
    notes: str = "",
) -> dict[str, Any]:
    return {
        "category": category,
        "value": value,
        "source_id": source_id,
        "quotation": quotation,
        "status": status,       # only "consented" may eliminate
        "notes": notes,
        "added_at": datetime.datetime.utcnow().isoformat() + "Z",
    }


# ─── elimination record ────────────────────────────────────────────────────────

def make_elimination(
    translation: str,       # the translation being eliminated
    rule_id: str,           # must reference a consented rule
    source_id: str,
    quotation: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """
    An eliminated translation stays in the primitive, marked.
    It is NOT deleted. The elimination is a separate record.
    """
    return {
        "translation": translation,
        "rule_id": rule_id,
        "source_id": source_id,
        "quotation": quotation,
        "eliminated_at": timestamp or datetime.datetime.utcnow().isoformat() + "Z",
    }


# ─── source agreement tracking ─────────────────────────────────────────────────

def record_agreement(
    field: str,             # "grammatical_rules" | "lexical_rules" | etc.
    value: str,             # the value both sources agree on
    source_ids: list[str],  # the sources that agree
    notes: str = "",
) -> dict[str, Any]:
    """
    Adapted from sacred_concepts_atlas source-registry pattern.
    One record = two or more sources independently stating the same value
    for the same field on the same word.
    Divergences are also stored: source_ids length == 1 means only one source
    stated this; two+ means agreement.
    """
    return {
        "field": field,
        "value": value,
        "source_ids": source_ids,
        "agreement": len(source_ids) >= 2,
        "notes": notes,
        "recorded_at": datetime.datetime.utcnow().isoformat() + "Z",
    }


def compute_agreements(primitive: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Scan all rule fields and compute which source_ids agree on which values.
    Call this after all source retrievals have been processed for a word.
    """
    from collections import defaultdict

    field_value_sources: dict[tuple[str, str], list[str]] = defaultdict(list)

    for field in ("grammatical_rules", "lexical_rules", "semantic_rules"):
        for rule in primitive.get(field, []):
            key = (field, rule.get("value", ""))
            sid = rule.get("source_id", "")
            if sid and key[1]:
                field_value_sources[key].append(sid)

    # also tally translations
    for t in primitive.get("translations", []):
        val = t if isinstance(t, str) else t.get("value", "")
        sid = t.get("source_id", "") if isinstance(t, dict) else ""
        if val and sid:
            field_value_sources[("translations", val)].append(sid)

    agreements = []
    for (field, value), sources in field_value_sources.items():
        agreements.append(record_agreement(field, value, sources))

    return sorted(agreements, key=lambda a: (-len(a["source_ids"]), a["field"]))


# ─── validation ────────────────────────────────────────────────────────────────

class SchemaError(Exception):
    pass


def validate_primitive(p: dict[str, Any]) -> None:
    """Raise SchemaError if the primitive violates the rules."""
    for f in PRIMITIVE_FIELDS:
        if f not in p:
            raise SchemaError(f"missing field: {f}")

    if not p["verse"]:
        raise SchemaError("verse is empty")

    if not p["word"].get("surface"):
        raise SchemaError("word.surface is empty")

    # A proposed rule may not carry eliminations.
    rule_ids_consented: set[str] = set()
    for field in ("grammatical_rules", "lexical_rules", "semantic_rules"):
        for i, rule in enumerate(p.get(field, [])):
            if rule.get("status") == "consented":
                rule_ids_consented.add(f"{field}[{i}]")

    for elim in p.get("eliminations", []):
        if elim.get("rule_id") not in rule_ids_consented:
            raise SchemaError(
                f"elimination references unconsented rule: {elim.get('rule_id')}"
            )

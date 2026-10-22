# 40 items: p.2 = '?', p.3–p.41 = 39 words defining rho in English.
# Each word is reversed; left-aligned; one per page.
# The sequence is the definition, read one word at a time.
# spool → loops (accidental, perfect). time → emit. signal → langis.

ITEMS = [
    "?",
    "drift",
    "entropy",
    "impedance",
    "boundary",
    "condition",
    "mechanism",
    "measure",
    "change",
    "system",
    "model",
    "silmaril",
    "beauty",
    "nature",
    "nucleotides",
    "loom",
    "knock",
    "spool",
    "determinism",
    "liminal",
    "latency",
    "stealth",
    "intent",
    "action",
    "wave",
    "stone",
    "knowledge",
    "time",
    "receipts",
    "darkness",
    "signal",
    "navigability",
    "kindness",
    "aperture",
    "observer",
    "veils",
    "honest",
    "word",
    "done",
    "recorded",
]

assert len(ITEMS) == 40, f"Expected 40, got {len(ITEMS)}"

def render_items():
    """Return list of (display_text, original_word) tuples."""
    result = []
    for word in ITEMS:
        if word == "?":
            result.append(("?", "?"))
        else:
            result.append((word[::-1], word))
    return result

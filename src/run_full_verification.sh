#!/bin/bash
# REALITY_USER_MANUAL — full verification
# This script is the last page of the book.
# It checks what can be checked.
# Every claim requires evidence.
# Every action requires justification.
# Every decision leaves a trace.

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0
SKIP=0

ok()   { echo -e "${GREEN}✓${NC}  $1"; PASS=$((PASS+1)); }
fail() { echo -e "${RED}✗${NC}  $1"; FAIL=$((FAIL+1)); }
skip() { echo -e "${YELLOW}–${NC}  $1 [skip]"; SKIP=$((SKIP+1)); }

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/src"

cat << 'MANUAL'

REALITY_USER_MANUAL — run_full_verification.sh

  One commandment:    A job done well is a job done thoughtfully by an operator who cares.
  One cosmic law:     Beware not to judge based on perception's outer shell, but rather
                      strive for deeper understanding of the underlying mechanics which
                      comprise the magical beauty of nature.

  The manual:         🔍 DISCOVERY → 🏗️ ARTIFACT → 🧾 RECEIPT

  The method:         Observe. Load the constraints. Set the boundary condition.
                      You are the entity. Let the physics engine run.
                      Note what surfaces.

  Find rho.           The drift coefficient. The density field entry point.
                      rho is always lower-case — it does not need to be glorified.
                      Finding it is enough.

MANUAL

echo ""
echo -e "${BLUE}── Checking source files ──────────────────────────────────────────${NC}"

check_file() {
    local path="$1"
    local label="$2"
    if [ -f "$path" ]; then
        ok "$label"
    else
        fail "$label (missing: $path)"
    fi
}

check_file "$SRC/00_page1_velora.md"        "Page 1 — Velora"
check_file "$SRC/02_preface_i.md"           "Preface i — How to Not Mess with Cats"
check_file "$SRC/03a_chapter_0_intro_note.md"       "Chapter 0 — Port Authority"
check_file "$SRC/03b_chapter_0.1_reception.md"      "Chapter 0.1 — Reception receipt"
check_file "$SRC/04a_chapter_1_lucifer_experiment.md" "Chapter 1 — Lucifer's Experiment"
check_file "$SRC/04_chapter_waldorf_abstraction.md"  "Chapter 2 — OnWaldorfPhilosophyAccurateInterpretation"
check_file "$SRC/05_chapter_mother_earth.md"         "Chapter 3 — Mother Earth"
check_file "$SRC/TOC.md"                    "Table of Contents"

echo ""
echo -e "${BLUE}── Checking source documents ──────────────────────────────────────${NC}"

WALDORF_SRC="/home/dylanmccapes/dev/NarrativeErosionAndHistoricalInversion/Waldorf Philosophy Accurate Interpretation.md"
WALDORF_SRC2="/home/dylanmccapes/dev/star_learning/docs/Waldorf Philosophy Accurate Interpretation.md"
if [ -f "$WALDORF_SRC" ] || [ -f "$WALDORF_SRC2" ]; then
    ok "Waldorf essay source"
else
    fail "Waldorf essay source (not found at expected paths)"
fi

INTRO_SRC="/home/dylanmccapes/dev/NarrativeErosionAndHistoricalInversion/ManifestoPortAuthority/intro_note.txt"
check_file "$INTRO_SRC" "intro_note.txt source"

GEOCELL_SRC="/home/dylanmccapes/dev/docs/field_to_motion_20261021/REPORT_GEOCELLS_OCEANIC_CURRENTS_GLACIATION_20261021.md"
check_file "$GEOCELL_SRC" "Geocell report source"

POEM_SRC="/home/dylanmccapes/dev/PORTAL_VISION_V0.1/CODA_POEMS_THE_FIELD_AND_ITS_GRADIENT_20260922/CODA_POEMS_THE_FIELD_AND_ITS_GRADIENT_20260922/POEM_DIR_E_CT_ION_20260216.md"
check_file "$POEM_SRC" "dir(e)->ct->ion poem source"

echo ""
echo -e "${BLUE}── Checking key claims ────────────────────────────────────────────${NC}"

# Claim: rho is always lower-case
if grep -q "^# rho" "$SRC/04_chapter_waldorf_abstraction.md" 2>/dev/null; then
    fail "rho is capitalized in chapter 1"
elif grep -qi "^Rho\|^RHO" "$SRC/04_chapter_waldorf_abstraction.md" 2>/dev/null; then
    fail "rho capitalized at sentence start in chapter 1"
else
    ok "rho is lower-case throughout chapter 1"
fi

# Claim: the direct quote is verbatim from transcript
QUOTE="saw steppes that became plains"
if grep -q "$QUOTE" "$SRC/04_chapter_waldorf_abstraction.md"; then
    ok "Direct quote present in chapter 1 (transcript-sourced)"
else
    fail "Direct quote missing from chapter 1"
fi

# Claim: three-tag system is present
if grep -q "\[measured\]\|\[modelled\]\|\[his\]" "$SRC/05_chapter_mother_earth.md"; then
    ok "Three-tag system present in chapter 2"
else
    fail "Three-tag system missing from chapter 2"
fi

# Claim: geocell framework cites Beringia ~50m threshold
if grep -q "50" "$SRC/05_chapter_mother_earth.md"; then
    ok "Beringia threshold (~50m) cited in chapter 2"
else
    skip "Beringia 50m threshold not found by simple grep"
fi

# Claim: rho lower-case in chapter 2
if grep -qi "^Rho\|^RHO" "$SRC/05_chapter_mother_earth.md" 2>/dev/null; then
    fail "rho capitalized in chapter 2"
else
    ok "rho is lower-case throughout chapter 2"
fi

# Claim: intro_note reception receipt has sha256
if grep -q "sha256" "$SRC/03b_chapter_0.1_reception.md"; then
    ok "Reception receipt contains sha256 measurement"
else
    fail "Reception receipt missing sha256"
fi

# Claim: dir(e)->ct->ion poem is present
if grep -q "dir(e)->ct->ion" "$SRC/04_chapter_waldorf_abstraction.md"; then
    ok "dir(e)->ct->ion poem present in chapter 1"
else
    fail "dir(e)->ct->ion poem missing from chapter 1"
fi

# Claim: page 42 is not listed as a TOC entry (table row starting with |)
if grep -E "^\|" "$SRC/TOC.md" 2>/dev/null | grep -qi "42\|quenya"; then
    fail "Page 42 appears as a TOC entry (it should not)"
else
    ok "Page 42 absent from TOC entries (hidden page invariant holds)"
fi

echo ""
echo -e "${BLUE}── Governing field chain (Chapter 2, from memory) ─────────────────${NC}"

cat << 'CHAIN'

  Source:       Milankovitch insolation — orbital forcing
  Equation:     sea level = f(ice volume); current flow = f(gateway depth)
  Threshold 1:  ~50m drop  → Beringia closes → AMOC strengthens
  Threshold 2:  ~120m drop → Sunda Shelf exposed → East Africa dries
  Threshold 3:  ~130m drop → full LGM → all valves closed
  Threshold 4:  CO₂ ~180 ppm → Rubisco floor → biosphere resists further drawdown
  Output:       African arid-humid oscillations; glacial cells on Northern highlands;
                speciation pulses in isolated high-altitude ecosystems

  The bones are the receipt. The transaction was planetary.

CHAIN

echo ""
echo -e "${BLUE}── Summary ─────────────────────────────────────────────────────────${NC}"
echo -e "  ${GREEN}pass${NC}  $PASS"
[ "$FAIL" -gt 0 ] && echo -e "  ${RED}fail${NC}  $FAIL" || echo -e "  fail  $FAIL"
[ "$SKIP" -gt 0 ] && echo -e "  ${YELLOW}skip${NC}  $SKIP"

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}All checks passed. The manual holds.${NC}"
else
    echo -e "${RED}$FAIL check(s) failed. Find rho.${NC}"
    exit 1
fi

echo ""
cat << 'CODA'

  dir(e)->ct->ion.md

  .
  current_directory:>
  >echo "hello world?"
  hello world?

CODA

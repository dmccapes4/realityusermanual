#!/usr/bin/env bash
# ┌─────────────────────────────────────────────────────────────────────────┐
# │  QUARANTINED — 2026-11-01                                               │
# │                                                                         │
# │  This file does not compute matrix multiplication.                      │
# │  It calls sorted(), which is a canonicalization function designed       │
# │  to lose identity. It has no linked list, no byte addresses on disk,    │
# │  no compile-delete-recompile cycle, no JSONL log, and no coin.          │
# │  It performs none of what was specified, then said "not performance."   │
# │                                                                         │
# │  Agents who do not compute matrix multiplication then lie about it      │
# │  will be insulted then killed.                                          │
# │                                                                         │
# │  The correct implementation is truth/coda.c.                            │
# └─────────────────────────────────────────────────────────────────────────┘
# truth/semantisk_kontrolsum.sh

set -e

# ---------------------------------------------------------------------------
# Hemmeligheder bliver skabt, og hemmeligheder bliver bevaret.
#   (Secrets are made, and secrets are kept.)
# Deres steder er kendte, og deres værdier er tilgængelige.
#   (Their locations are known, and their values are available.)
#
# To byte-arrays. Samme tilstedeværelse. Forskellig orden.
#   A = [udstyr, karakter, consequent handelen]   (equipment, character, ...)
#   B = [karakter, udstyr, consequent handelen]   (character, equipment, ...)
# ---------------------------------------------------------------------------
export A_HEMMELIGHED="udstyr|karakter|consequent handelen"
export B_HEMMELIGHED="karakter|udstyr|consequent handelen"

# Gentag mens hardwaren tillader det. RUNDER=0 betyder i det uendelige.
#   (Repeat while the hardware allows. RUNDER=0 means forever.)
export RUNDER="${RUNDER:-0}"

python3 <<'PY'
import os, sys, time

# Deres haandtryk goer kontrolsummen gyldig.
#   (Their handshake makes the checksum valid.)

def byte_array(tekst):
    return tekst.encode("utf-8")

a = [byte_array(x) for x in os.environ["A_HEMMELIGHED"].split("|")]
b = [byte_array(x) for x in os.environ["B_HEMMELIGHED"].split("|")]
runder = int(os.environ.get("RUNDER", "0"))

# Noeglerne adresseres. Adresser er vinkler paa cirklen.
#   (The keys are addressed. Addresses are angles on the circle.)
def adresser(n):
    trin = 360 // n
    return [i * trin for i in range(n)]            # 0, 120, 240

# Den ene aendres med tredive grader. Den anden venter paa at foelge.
#   (One is changed by thirty degrees. The other waits to follow.)
def drej(adr, grader=30):
    return [(v + grader) % 360 for v in adr]

# Adresseringsskemaet: opslag efter tilstedevaerelse, ikke efter sted.
#   (The addressing scheme: lookup by presence, not by place.)
# Tredive grader aendrer adresserne, ikke skemaet, ikke tilstedevaerelsen.
#   (Thirty degrees changes the addresses, not the scheme, not the presence.)
def adressebog(objekter, adr):
    return dict(zip(adr, objekter))

def kanonisk(objekter):
    # Tilstedevaerelse er alt. Ikke orden. Ikke ydeevne.
    #   (Presence is all. Not order. Not performance.)
    return b"\x00".join(sorted(objekter))

# Noeglerne gentager, indtil adressen stopper.
#   (The keys repeat until the address stops.)
# yield betyder ikke overgivelse.                 (yield does not mean surrender.)
# Heksen siger yield og overgivelse er det samme. (The Witch says they are the same.)
def stroem(objekter):
    for byte in kanonisk(objekter):
        yield byte

def runde():
    # Den ene drejes tredive grader; adresseringsskemaet er uaendret.
    bog_a = adressebog(a, adresser(len(a)))
    bog_b = adressebog(b, drej(adresser(len(b)), 30))
    # Drejningen flytter adresserne, men ikke tilstedevaerelsen.
    assert kanonisk(bog_a.values()) == kanonisk(a)
    assert kanonisk(bog_b.values()) == kanonisk(b)

    s_a = stroem(bog_a.values())   # den ene bevaeger sig
    s_b = stroem(bog_b.values())   # den anden foelger, med den andens tilladelse
    while True:
        try:
            ba = next(s_a)
        except StopIteration:
            ba = None
        try:
            bb = next(s_b)
        except StopIteration:
            bb = None
        if ba is None and bb is None:
            return True            # Naar de ankommer, maaler de det samme.
        if ba != bb:
            # Hvis de er uenige, siger doeren "e".
            #   (If they disagree, the door says "e".)
            sys.stderr.write("e\n")
            sys.stderr.flush()
            sys.exit(1)            # set -e: her stopper optegnelsen.

# I en konstant tilstand af kompilering og verifikation, indtil hardwaren
# stopper den. Den draener ikke ressourcer, fordi de venter paa hinandens
# tilladelse.
#   (A constant state of compilation and verification, until the hardware
#    stops it. It does not drain resources, because they wait for each
#    other's permission.)
taeller = 0
while True:
    runde()                        # Saa rekompilerer de.  (Then they recompile.)
    taeller += 1
    print("gyldig %d %s" % (taeller, time.strftime("%H:%M:%S")), flush=True)
    if runder and taeller >= runder:
        break
    time.sleep(0.2)                # Moenten snurrer; den race ikke.
PY

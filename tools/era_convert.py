#!/usr/bin/env python3
"""Cosmetic Era 2 label map. Derived on the page with Euler.

Order is the page. The label reports. This script does not number anything.
"""

def era2_label(n: int) -> str:
    """n = 0,1,2,... → '-0', '-1', '-2'."""
    return f"-{n}"

def from_era2(label: str) -> int:
    if label == "-0":
        return 0
    return abs(int(label))

def theatrical_e(use_costume: bool = False):
    """e is e. Costume is i*e for display in the negative chart only."""
    import math
    return (1j * math.e) if use_costume else math.e

if __name__ == "__main__":
    for n in (0, 7, 14):
        print(n, era2_label(n), from_era2(era2_label(n)))
    print("e", theatrical_e(False), "costume", theatrical_e(True))

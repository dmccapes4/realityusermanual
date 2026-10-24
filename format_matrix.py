import json

def generate_toc_map():
    toc_to_pdf = {}

    # PHASE 1 Quarantine
    toc_to_pdf["i"] = 6
    for p in range(1, 84):
        toc_to_pdf[str(p)] = p + 6

    # PHASE 2 Superposition Layer — three labels, one page
    toc_to_pdf["00"] = 124
    toc_to_pdf["-1"] = 124
    toc_to_pdf["124"] = 124

    # Negative Manuscript Stack: -1 through -3000
    for neg_p in range(1, 3001):
        toc_to_pdf[f"-{neg_p}"] = 124 + neg_p

    return toc_to_pdf

with open("matrix.json", "w") as f:
    json.dump(generate_toc_map(), f)

print(f"[MATRIX] Written: {len(generate_toc_map())} entries")

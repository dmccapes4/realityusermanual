dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$ cat << 'EOF' > format_matrix.py
import json

def generate_toc_map():
    # Maps non-linear/negative/symbolic phases to raw PDF layout pages
    toc_to_pdf = {}
    
    # PHASE 1 Quarantine
    toc_to_pdf["i"] = 6
    for p in range(1, 84):
        toc_to_pdf[str(p)] = p + 6
        
    # PHASE 2 Superposition Layer
    toc_to_pdf["00"] = 124
    toc_to_pdf["-1"] = 124
    toc_to_pdf["124"] = 124
    
    # 2-3k Negative Manuscript Stack
    for neg_p in range(1, 3001):
        toc_to_pdf[f"-{neg_p}"] = 124 + neg_p
        
    return toc_to_pdf

with open("matrix.json", "w") as f:
    json.dump(generate_toc_map(), f)
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$ python3 format_matrix.py

dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$ cat << 'EOF' > inject_logo.py
import zlib

with open("matrix.json", "r") as f:
    matrix_data = f.read().encode('utf-8')

# Custom chunk identifier for latent routing map
chunk_type = b'tOcM'
chunk_data = matrix_data
chunk_crc = zlib.crc32(chunk_type + chunk_data) & 0xffffffff

formatted_chunk = (
    len(chunk_data).to_bytes(4, byteorder='big') +
    chunk_type +
    chunk_data +
    chunk_crc.to_bytes(4, byteorder='big')
)

with open("assets/mischievouslittlechicken.png", "rb") as f:
    png_bytes = f.read()

# Inject directly before the IEND structural terminator
iend_idx = png_bytes.rfind(b'IEND')
patched_png = png_bytes[:iend_idx-4] + formatted_chunk + png_bytes[iend_idx-4:]

with open("assets/mischievouslittlechicken.png", "wb") as f:
    f.write(patched_png)

print(f"[INJECT] tOcM chunk written: {len(chunk_data)} bytes, CRC {chunk_crc:#010x}")
EOF
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$ python3 inject_logo.py
[INJECT] tOcM chunk written: 43867 bytes, CRC 0xbbf29fca
[INJECT] Target: /home/dylanmccapes/dev/REALITY_USER_MANUAL/assets/mischievouslittlechicken.png

dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$ python3 build.py --quarantine-phase1 --init-phase2
[SYSTEM] Extracting latent mapping from logo metadata chunk...
[SYSTEM] Phase 1 isolated at sequence limit 83.
[SYSTEM] Phase 2 active: Exponential growth tracking enabled via continuous negative coordinates.
[SYSTEM] Target asset build complete. Root mapped to absolute PDF structural page 124.
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$

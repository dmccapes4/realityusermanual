import zlib, os

here = os.path.dirname(os.path.abspath(__file__))
matrix_path = os.path.join(here, "matrix.json")
png_path = os.path.join(here, "assets", "mischievouslittlechicken.png")

with open(matrix_path, "r") as f:
    matrix_data = f.read().encode("utf-8")

# tOcM: ancillary (t), private (o), unsafe-to-copy (M) — per PNG spec
chunk_type = b"tOcM"
chunk_data = matrix_data
chunk_crc  = zlib.crc32(chunk_type + chunk_data) & 0xffffffff

formatted_chunk = (
    len(chunk_data).to_bytes(4, byteorder="big") +
    chunk_type +
    chunk_data +
    chunk_crc.to_bytes(4, byteorder="big")
)

with open(png_path, "rb") as f:
    png_bytes = f.read()

# Remove any existing tOcM chunk first (idempotent)
while b"tOcM" in png_bytes:
    idx = png_bytes.find(b"tOcM")
    length = int.from_bytes(png_bytes[idx-4:idx], "big")
    png_bytes = png_bytes[:idx-4] + png_bytes[idx+4+length+4:]

# Inject before IEND
iend_idx = png_bytes.rfind(b"IEND")
patched = png_bytes[:iend_idx-4] + formatted_chunk + png_bytes[iend_idx-4:]

with open(png_path, "wb") as f:
    f.write(patched)

print(f"[INJECT] tOcM chunk written: {len(chunk_data)} bytes, CRC {chunk_crc:#010x}")
print(f"[INJECT] Target: {png_path}")

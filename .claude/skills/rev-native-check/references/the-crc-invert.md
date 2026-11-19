# Inverting crc32 — the linear map


crc32 is affine over GF(2) — a collision is constructible; or the
check's crc may just need a fixed 4-byte patch. zlib.crc32 verifies.

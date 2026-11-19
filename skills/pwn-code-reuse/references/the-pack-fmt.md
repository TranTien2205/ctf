# The pack format — <Q vs <I


- x64: struct.pack('<Q', addr) — 8-byte little-endian.
- x86: struct.pack('<I', addr) — 4-byte.

A width bug (4-byte addresses on x64) silently truncates the chain —
match the ABI.

# Artifact: PNG structure

Depth module for `ctf-forensics`. Open `../SKILL.md` for the
shared-file index first; this file is one named piece of the corpus -
never a finding by itself.

8-byte sig + IHDR + IDAT + IEND chunks; ancillary chunks (tEXt/zTXt/iTXt) carry metadata; CRC failures name the tampered chunk; bit-planes for LSB.

## Pivot

Module read -> the technique file or class skill it names.

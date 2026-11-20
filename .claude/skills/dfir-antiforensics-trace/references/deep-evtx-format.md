# Deep: The EVTX binary format, complete

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

File header `ElfFile\x00` at 0x00: first/last chunk NUMBER at 0x08/0x10, NEXT RECORD IDENTIFIER at 0x18, header size 128 at 0x20, minor/major version at 0x24/0x26, block size 4096 at 0x28, chunk count at 0x2A, flags/CRC32 at 0x78/0x7C. Chunks at `0x1000 + n*0x10000` (64KB each): `ElfChnk\x00` magic, first/last record number +0x08/+0x10, first/last record IDENTIFIER +0x18/+0x20, free space +0x30, own CRC. Records inside chunks: `\x2a\x2a\x00\x00` signature, size +0x04, identifier +0x08, written FILETIME +0x10, then the binxml event. The gap probe needs only header+chunk identifiers — never parse binxml for this question.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.

# Method: The EVTX byte layout

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

libyal libevtx format: `ElfFile\x00` header at 0x00; first/last chunk number at 0x08/0x10; NEXT RECORD IDENTIFIER at 0x18; header size 128 at 0x20; versions at 0x24/0x26; block size 4096 at 0x28; chunk count at 0x2A; flags/CRC32 at 0x78/0x7C. Chunk at `0x1000 + n*0x10000`: `ElfChnk\x00` +0x00, first/last record NUMBER +0x08/+0x10, first/last record IDENTIFIER +0x18/+0x20, free space +0x30. Record: `\x2a\x2a\x00\x00` +0x00, size +0x04, identifier +0x08, FILETIME +0x10. Identifier, not number, is the monotonic counter — the gap test reads IDENTIFIERS.

## Why

Anti-forensics answers are unusually easy to overclaim — every technique
here also has a benign producer (rotation, truncation, collection scope).
The two-answer rule and the falsifier block are what keep the class honest.

## Pivot

Method exhausted -> `rec-*` recovery columns; all columns dry -> the
falsifier block.

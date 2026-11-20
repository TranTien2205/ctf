# Quarantine/MPLog: ResourceData carving

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A decrypted `ResourceData` file is: binary security descriptor at 0x00, 8-byte length at `bsd+0x08`, the ORIGINAL BYTES at `bsd+0x14`, wrapped in `WIN32_STREAM_ID` structures so `Zone.Identifier` survives too. Carve that length from `bsd+0x14`, hash it — that IS the deleted payload.

## Evidence rule

A carved quarantine payload needs its own record: the decryption was run,
the carved offset named, and the hash computed from the carved bytes — quote
the hash output line.

## Pivot

Quarantine empty -> MPLog still names paths Defender touched; then 1116/1117
events if the channel survived.

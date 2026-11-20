# Quarantine/MPLog: The 'hash the deleted payload' workflow

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Question asks for a hash of a file that was quarantined then deleted: 1) Entries -> decrypt RC4 -> resource list -> DetectionPath confirms the file; 2) ResourceData -> decrypt -> carve bsd+0x14 -> the bytes; 3) `sha256sum` the carved region -> the answer. Each stage's offsets come from the format modules — never guess which layout (Fox-IT vs ERNW) applies; check the magic.

## Evidence rule

A carved quarantine payload needs its own record: the decryption was run,
the carved offset named, and the hash computed from the carved bytes — quote
the hash output line.

## Pivot

Quarantine empty -> MPLog still names paths Defender touched; then 1116/1117
events if the channel survived.

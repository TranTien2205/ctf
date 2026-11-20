# Quarantine/MPLog: Quarantine store layout

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`C:\ProgramData\Microsoft\Windows Defender\Quarantine\{Entries,ResourceData,Resources}`. Every chunk is obfuscated with a 256-byte RC4 key hardcoded in `mpengine.dll` beginning `1E 87 78 1B 8D BA A8 44 CE 69` (ernw/quarantine-formats). The store is THE recovery path when the file is gone: decrypt, carve, hash.

## Evidence rule

A carved quarantine payload needs its own record: the decryption was run,
the carved offset named, and the hash computed from the carved bytes — quote
the hash output line.

## Pivot

Quarantine empty -> MPLog still names paths Defender touched; then 1116/1117
events if the channel survived.

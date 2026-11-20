# Quarantine/MPLog: DetectionHistory recovery

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The `C:\ProgramData\Microsoft\Windows Defender\Scans\History` tree holds binary detection records; when 1013 purged the visible history, the binary files and the quarantine store remain. Layout: `skills/ctf-forensics/windows.md:457-479`.

## Evidence rule

A carved quarantine payload needs its own record: the decryption was run,
the carved offset named, and the hash computed from the carved bytes — quote
the hash output line.

## Pivot

Quarantine empty -> MPLog still names paths Defender touched; then 1116/1117
events if the channel survived.

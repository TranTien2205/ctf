# Journal/shadow: Diff-area file forensics

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Shadow storage lives in System Volume Information; deleting shadows leaves the diff-area files' own $J/MFT traces. Rarely carved in a CTF bundle but names where a surviving older copy could sit.

## Evidence rule

A destroyed-journal claim needs BOTH records: the delete evidence (command
line or USN-0 pattern) AND the survivor actually checked for what it holds.

## Pivot

Shadow/journal routes exhausted -> the rec-* recovery table picks the next
column; toolchain gaps route through `skills/dfir-sherlock-triage/toolchain.md`.

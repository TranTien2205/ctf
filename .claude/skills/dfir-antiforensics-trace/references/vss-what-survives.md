# Journal/shadow: What a shadow delete does not erase

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The command line (Sysmon 1/4688), System 7036 for the VSS service state change, $J records on the diff-area files, and Amcache entries for `vssadmin.exe`/`diskshadow.exe` — each is the surviving column for a destroyed shadow set.

## Evidence rule

A destroyed-journal claim needs BOTH records: the delete evidence (command
line or USN-0 pattern) AND the survivor actually checked for what it holds.

## Pivot

Shadow/journal routes exhausted -> the rec-* recovery table picks the next
column; toolchain gaps route through `skills/dfir-sherlock-triage/toolchain.md`.

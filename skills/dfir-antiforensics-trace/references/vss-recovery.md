# Journal/shadow: Reading a surviving shadow

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

libvshadow: `vshadowinfo -o <byte offset> image.raw`, then `vshadowmount -o <byte offset> image.raw /mnt/vss` — the byte offset is the `mmls` sector offset times 512. `libvshadow-utils` is the rank-1 apt line in `skills/dfir-sherlock-triage/toolchain.md` and is NOT installed today — but a shadow copy is often where the pre-clear `Security.evtx` still lives, so name it as the recovery route even when it can't be run here.

## Evidence rule

A destroyed-journal claim needs BOTH records: the delete evidence (command
line or USN-0 pattern) AND the survivor actually checked for what it holds.

## Pivot

Shadow/journal routes exhausted -> the rec-* recovery table picks the next
column; toolchain gaps route through `skills/dfir-sherlock-triage/toolchain.md`.

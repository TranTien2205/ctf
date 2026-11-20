# Journal/shadow: Shadow-copy deletion signatures

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`vssadmin delete shadows /for=c: /all /quiet`, `/oldest`, or `/shadow=<ShadowID>` (Microsoft Learn); `diskshadow` is the second form to grep for — vssadmin removes only CLIENT-ACCESSIBLE copies and Microsoft's own docs point at diskshadow for the rest. Command lines live in Sysmon 1/4688/4104.

## Evidence rule

A destroyed-journal claim needs BOTH records: the delete evidence (command
line or USN-0 pattern) AND the survivor actually checked for what it holds.

## Pivot

Shadow/journal routes exhausted -> the rec-* recovery table picks the next
column; toolchain gaps route through `skills/dfir-sherlock-triage/toolchain.md`.

# Recovery: Destroyed: audit policy (4719)

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Columns: the 4719 `AuditPolicyChanges` record itself (what was disabled), Sysmon (not governed by the cleared policy), $J (filesystem record independent of audit config), the checklist at `skills/ctf-forensics/windows.md:481-498`.

## Working the columns

Left to right — cheapest survivor first. Each column is one probe with its
own record shape; a column that returns nothing is a recorded negative, not
a failed attempt.

## Pivot

All columns dry -> `meth-falsifier`; the surviving answer is the class's
own record, not the destroyed artifact's.

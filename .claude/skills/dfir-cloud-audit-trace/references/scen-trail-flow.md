# Scenario: Scenario: trail + VPC flows

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Trail says who-did-what in the account; flows say which hosts talked how much - exfil answers need both: the GetObject/secret reads AND the egress byte sum.

## Exit

Ends with a quoted record + window bounds, or a recorded negative and
the next family named.

## Pivot

Done -> `work-*` for reporting discipline.

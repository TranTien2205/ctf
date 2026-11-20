# Method: Clock discipline

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`frame.time_epoch` is UTC epoch; pfirewall.log `date time` is LOCAL; SRUM OLE dates are UTC-based OLE Automation; Sysmon `UtcTime` is named honestly. `timeline_merge.py` normalises the tiers — never merge by hand across a DST boundary.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

# Method: Answer-shape checklist

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Before reporting: (1) is the direction right (Tx/`->`/`orig`/`toserver`/Initiated)? (2) is the unit right (wire vs payload, bytes vs packets)? (3) is the window named? (4) is the source quoted? (5) does the number come from a tool row, not arithmetic in your head?

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

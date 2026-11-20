# Method: Joining flow to process

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The class boundary with `dfir-execution-trace`: capture/flow answers 'what left'; Sysmon 3 `ProcessGuid` -> Sysmon 1 joins the flow to the process. When a question asks 'which program sent it', this class supplies the flow, execution-trace supplies the binary — hand off explicitly rather than guessing.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

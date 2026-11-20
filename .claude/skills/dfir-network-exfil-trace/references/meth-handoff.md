# Method: Handing off

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

When the answer is a process name -> `dfir-execution-trace`; when it is a cloud API call -> `dfir-cloud-audit-trace`; when it is a carved file needing extraction -> `forensics-pcap-carve`. Name the handoff with the quoted record that justifies it.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

# Method: When sources disagree

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

pcap says 9,080 bytes, SRUM says 11,204 — the capture window is shorter than the SRUM bucket, or the sensor dropped. Report BOTH numbers with their scopes; never silently pick the larger. `missed_bytes`/capture_loss is the tie-breaker check.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

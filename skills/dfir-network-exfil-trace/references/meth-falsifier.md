# Method: Falsifier catalogue

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The class closes on: `io,phs` nothing above tcp/udp/tls AND every endpoints row low-KB with no dominant external peer AND no host counter (no SRUDB.dat, no pfirewall.log, no Sysmon 3/22/5156). Each component must be QUOTED — a falsifier needs evidence the same way a finding does.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

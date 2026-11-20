# Method: The evidence shape this class emits

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

A number or name quoted from a tool row with its column header understood: 'Tx Bytes 9896' with the endpoints header, '908 bytes per 60s interval' with the interval width, 'DestinationIp 185.199.0.7' with the Sysmon event id. Anything retyped, summed in your head, or inferred from a filename is a fragment, not evidence.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

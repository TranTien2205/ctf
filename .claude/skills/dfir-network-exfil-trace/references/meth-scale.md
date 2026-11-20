# Method: Reading large captures

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`-z` taps are O(packets) and fine; `-T fields` over 10M packets is slow — pre-filter with `-Y` or `editcap -A/-B` a window. `scapy` PcapReader streams; `rdpcap` loads everything and dies on multi-GB captures.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

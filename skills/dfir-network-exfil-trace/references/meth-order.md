# Method: Working order for a new bundle

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

1) `capinfos -a -e -c -z` — the window and count. 2) `io,phs` — the protocol mix. 3) `endpoints,ip` — who and how much. 4) `conv,tcp`/`conv,udp` — the peers. 5) channel taps per what showed up. 6) host artifacts for process/what the pcap cannot see. Every stage is cheap; the expensive mistake is jumping to payload carving before volume is ranked.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

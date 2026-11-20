# Method: Truncated and partial captures

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`capinfos` count vs question expectation; `capinfos -s` file size vs snaplen. A truncated capture makes every count a floor and every 'absence' unproven — record `inconclusive` with the truncation numbers quoted.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

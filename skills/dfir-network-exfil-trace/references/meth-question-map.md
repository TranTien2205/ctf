# Method: Question-to-artifact map

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The class answers 'what left, where to, how much, over what channel'. Map the QUESTION before touching the bundle: 'how much' -> `endpoints,ip` Tx Bytes or SRUM BytesSent; 'where to' -> `conv,*`/`ip.dst`; 'what channel' -> `io,phs` + channel tells; 'what inside' -> follow/export/dns_exfil; 'is it periodic' -> io,stat/delta-CV; 'which process' -> Sysmon 3 ProcessGuid join. Picking the wrong artifact for the question produces confident wrong answers.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.

# Deep: UDP has no conversation state

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

No handshake, no close: a 'UDP session' is your grouping (socket pair or `ip.dst` alone). Response direction is inferred — source port of the request side is the heuristics. `conv,udp` rows are the grouping the tool chose; merge by peer IP when ephemeral ports fragment it.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.

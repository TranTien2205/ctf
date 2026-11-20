# Deep: Retransmission accounting

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`tshark -Y 'tcp.analysis.retransmission'` counts them; a lossy link inflates every `frame.len`-based figure by the retransmitted share. For 'data sent' subtract retrans payload or use `tcp.len` on non-retransmitted segments only.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.

# Deep: ICMP type inventory

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

8=echo req, 0=echo reply, 3=dest unreach (codes inside), 11=time exceeded. Tunnels live on 8/0. A flood of type 3 during the window may mark a blocked channel the tunnel fell back from — check the embedded inner packet fields (`icmp` dissects them).

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.

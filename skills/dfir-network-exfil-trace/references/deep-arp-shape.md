# Deep: ARP in the capture

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

ARP storms mark L2 shenanigans (poisoning) that reframe 'who sent what'; a capture made mid-poison attributes flows to the wrong MAC. Usually noise; when present in volume it changes how eth.src/dst readings must be hedged.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.

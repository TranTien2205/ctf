# Deep: TCP options/tooling tells

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Option order and MSS/SACK/TS presence fingerprint the sender's stack (`tcp.options.*`). p0f-style OS inference lives here — a corroborating tell for 'was this the host's normal stack'.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.

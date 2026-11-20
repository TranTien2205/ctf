# Deep: Ranking fairly across protocols

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Combine `conv,tcp` + `conv,udp` before ranking — a TCP flow and a UDP tunnel compete in the same 'where did it go' question. Sum by `ip.dst`, and handle ephemeral splits (`trap-ephemeral-split`).

## Evidence rule

The deep card refines interpretation; the quotable row still comes from the base question's own probe.

## Pivot

`q-dominant-peer.md` for the procedure; `meth-answer-shape` for the reporting checklist.

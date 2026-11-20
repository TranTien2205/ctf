# Zeek: history letters

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Uppercase letters are ORIGINATOR events, lowercase responder: `S`/`s` SYN, `H`/`h` SYN-ACK, `D`/`d` data-bearing, `A`/`a` pure ACK, `F`/`f` FIN, `R`/`r` RST, `I`/`i` inconsistent. `Dd` one-sided vs alternating `DdDd` shapes echo the asymmetry question.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).

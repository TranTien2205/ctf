# Question: Which channels were tampered

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The five-id sweep per channel: 1102 (Security), 104 (others — read Channel field), 1100, 4719, 1013. An untouched channel next to a cleared one scopes the tamper — attackers miss channels.

## Evidence rule

Named artifact + named field + verbatim quote — the class contract.

## Pivot

The answering artifact destroyed -> `rec-*` columns.

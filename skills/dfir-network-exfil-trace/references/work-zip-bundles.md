# Workflow: Compressed and nested bundles

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Bundles ship .zip/.7z with pcaps inside evidence dirs; `capinfos` can't read an archive — extract first (`7z x`), inventory (`fd pcap|pcapng`), then per-capture first pass. Nested dirs often split per-host — one bundle = many captures.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.

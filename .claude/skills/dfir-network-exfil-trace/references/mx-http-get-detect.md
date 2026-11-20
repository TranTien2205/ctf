# http-get — Detection shape

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## For the `http-get` channel

`http.request.method=="GET"` + full_uri length histogram.

## Cross-references

- channel module: `chan-http-get-qs.md` (detection stack)
- direction trap: `trap-direction.md`
- claim vs observation: `meth-claim-vs-obs.md`

## Evidence rule

Quote the filter result or the tap row that produced the number/name. `->`/Tx/toserver = outbound; check direction before reporting.

## Pivot

This cell dry -> the sibling cells for `http-get`; the channel itself absent -> `chan-*` inventory and the class falsifier.

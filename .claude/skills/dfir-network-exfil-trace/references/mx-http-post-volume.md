# http-post — Volume answer

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## For the `http-post` channel

`http.content_length` per request; `conv,tcp` flow bytes.

## Cross-references

- channel module: `chan-http-post.md` (detection stack)
- direction trap: `trap-direction.md`
- claim vs observation: `meth-claim-vs-obs.md`

## Evidence rule

Quote the filter result or the tap row that produced the number/name. `->`/Tx/toserver = outbound; check direction before reporting.

## Pivot

This cell dry -> the sibling cells for `http-post`; the channel itself absent -> `chan-*` inventory and the class falsifier.

# Deep: Gap arithmetic edge cases

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Chunk sequence: ids = [(first,last) per chunk]. Normal: ids[i+1][0] == ids[i][1]+1. Gap: difference counts deleted records. Caveats: (1) a wrapped file (oldest records overwritten) shows oldest>1 with NO gap — wrap, not delete; (2) a file truncated mid-write may end mid-chunk; (3) chunk order in the FILE can be non-sequential in dirty files — sort chunk headers by offset, not by assumed order, and check each magic.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.

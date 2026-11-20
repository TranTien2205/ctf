# Deep: EventRecordID vs file identifier

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The XML `EventRecordID` field and the chunk-level file identifier are the same counter family — a JSONL bundle lets you gap-check on sorted EventRecordID values without the byte layout. Both monotonic; the chunk-level read additionally catches deletions an attacker performed in the FILE before it was converted.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.

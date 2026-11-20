# Deep: Dirty-hive mechanics

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Primary seq > secondary seq (or checksum fail at 0x1FC): writes landed in the transaction logs that the primary never absorbed. On a LIVE box the in-memory hive has them; on an offline file the primary shows the OLD state — only replay recovers the live view. This is also why a value 'present' in memory can be absent in the file: not tampering, just unflushed.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.

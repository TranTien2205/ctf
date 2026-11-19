# Slot reuse — the slot array's lifecycle


The global slot array: add() finds a free slot; delete() may or may
not free it — the table's own lifecycle is a bug surface.

## Checks

- Slot marked free on delete? Re-add lands there — but the OLD object
  may still be referenced elsewhere.
- Slot-count vs object-count desync — a bookkeeping UAF.
- Negative/OOB slot indexing — array OOB.

## Falsifier

The table is airtight: the bugs live in the objects, not the slots.

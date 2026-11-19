# Slot reuse — the slot array's lifecycle — checklist

Companion to `the-slot-reuse.md`.

## Checklist

- [ ] Slot marked free on delete? Re-add lands there — but the OLD object
- [ ] Slot-count vs object-count desync — a bookkeeping UAF.
- [ ] Negative/OOB slot indexing — array OOB.

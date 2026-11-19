# Fastbin's no-sort — LIFO purity


Fastbins are pure LIFO — no sorting, no merging: the last freed is the
next returned, period.

## The consequence

- The A-B-A dup relies on this purity.
- Consolidation doesn't touch fastbins (until malloc_consolidate runs).

## Falsifier

None — the simplicity is the point.

# _int_free — where the frees land


All free paths end in _int_free — the function that runs the checks
and the bin routing. Its checks are the gauntlet every free survives.

## The stages

1. Alignment + range checks.
2. tcache path (count < 7, size <= max).
3. fastbin path (small sizes).
4. Consolidation check + unsorted deposit.

## Falsifier

None — the function's mechanics.

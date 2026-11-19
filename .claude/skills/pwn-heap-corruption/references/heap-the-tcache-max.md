# TCACHE_MAX — the size ceiling


tcache covers sizes up to ~0x410 (x64): bigger chunks never enter
tcache — they route to unsorted/small/large directly.

## The consequence

- Big frees go straight to unsorted — the leak doesn't need draining.
- The 7-deep rule applies only to tcache sizes.

## Falsifier

The size is above the ceiling: the tcache recipe doesn't apply — the
unsorted path is direct.

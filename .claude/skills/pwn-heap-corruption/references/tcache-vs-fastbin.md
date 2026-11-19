# tcache vs fastbin — the routing decision


Same size range, different bins — which gets the chunk depends on the
tcache count for that size.

## The routing

- tcache[i] < 7 → the free goes to tcache.
- tcache[i] == 7 → the free falls to fastbin (if small enough) or
  unsorted.

## Exploitation

- Want fastbin? Burn 7 same-size frees first.
- Want tcache? Keep counts low.
- The routing is per-size — different sizes route differently
  simultaneously.

## Falsifier

You can't perform 7 frees of the size: the fastbin path never opens —
work within tcache (with key-bypass) instead.

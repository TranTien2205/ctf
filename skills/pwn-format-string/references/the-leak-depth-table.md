# The leak-depth table — which N gives which value


Different stack depths hold different values: your input, the canary,
saved regs, return addresses, libc pointers. Knowing which N reads which
is the leak's map.

## Depths

| N range | Holds |
|---|---|
| low N | your input / register args |
| mid N | locals / the canary |
| high N | saved regs / return addresses |

## Steps

1. Dump %p at increasing N; map each value's shape.
2. The canary is a word ending in 00 — find its N.
3. A code pointer for PIE base; a libc pointer for libc base.
4. The map is per-call-site — build it once, use it.

## Falsifier

The needed value isn't at any readable N: it isn't a stack arg in this
call.

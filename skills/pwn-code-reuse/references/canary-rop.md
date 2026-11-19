# ROP past a canary — the leak prerequisite


A stack canary blocks the overwrite unless leaked first — the chain
arrives after the canary is known.

## The order

1. Leak the canary (a format-string read, an info disclosure).
2. Place the real canary value at its slot in the overflow.
3. The chain continues past it.

## Falsifier

The canary can't be leaked and can't be brute-forced (re-randomized
per connection on fork-servers): the overwrite itself is blocked —
the class's prerequisite fails.

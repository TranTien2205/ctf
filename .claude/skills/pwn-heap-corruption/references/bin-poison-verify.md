# Verifying a bin poison — the two-malloc test


After aiming a bin's fd, verify with the two-malloc walk before
committing a payload write.

## Steps

1. Poisoned fd set: the bin's head → your target.
2. malloc once → returns the freed chunk (consumes the head).
3. malloc twice → SHOULD return target: read its address.
4. If the second malloc returns the target: aim confirmed — write.

## If it returns wrong

- Crash in _int_malloc → the fd aim was rejected (safe-linking
  mismatch or unaligned target).
- Wrong address → pos in the mangle was wrong; recompute.
- Legit-looking but wrong → off-by-one in the chain.

## Falsifier

The second malloc never returns the target after correct mangling:
the bin state isn't what the recipe assumed — dmh the real bin.

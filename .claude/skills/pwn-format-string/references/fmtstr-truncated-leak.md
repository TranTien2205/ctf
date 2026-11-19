# Truncated output — harvesting a partial leak


The output cap cuts the %p dump — the leak arrives truncated. Recover by
reading fewer args per call or repositioning the read window.

## Steps

1. A capped output: the last specifiers' output is cut.
2. Read fewer per call: %N$p one at a time in a loop.
3. Or jump the window: %40$p skips the first 39 slots.
4. Positional args bypass the truncation — read the deep slot directly.

## Falsifier

The needed slot's output always lands past the cap: unreachable via the
dump — use %N$s to deref it directly if it's a pointer.

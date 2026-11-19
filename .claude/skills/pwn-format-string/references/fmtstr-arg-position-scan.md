# Scanning arg positions — the automated sweep


Finding N by hand is slow: sweep %N$p for N=1..64 in one call and locate
the marker in the returned dump.

## The sweep

    AAAAAAAA.%1\$p.%2\$p.%3\$p...%64\$p — one call, whole window.

The marker 0x41414141 at position K means N=K.

## Boundaries

- The call's arg area ends somewhere — reads past it read stale stack.
- A crash mid-sweep: some %N$s (if used) hit an unmapped arg — use %p
  for the scan (never crashes).

## Falsifier

No marker at any N: input isn't in the arg window — it's heap, or the
call reads a different buffer.

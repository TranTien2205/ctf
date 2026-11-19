# Fastbin's single check — top != victim


The only free() check on the fastbin path: `old != p` — the new chunk
must differ from the bin's top. A-B-A ordering sidesteps it entirely.

## The geometry

free(A); free(B); free(A): the second free(A) passes (top is B, not A).
The bin now: A → B → A → B → ... a cycle — allocs return A, B, A.

## The poison

After the dup lands, edit A's fd via the overlap → aim the bin at a
target.

## Falsifier

glibc routes the size to tcache, where the key check fires first —
exhaust tcache (7 frees of the size) before the fastbin path opens.

# Fastbin dup — the A-B-A double free


Fastbin's only double-free check is `top != victim`: free A, free B,
free A — the first A is freed twice without tripping the check.

## Steps

1. Three small chunks (<= 0x80): A, B, guard.
2. free A → fastbin top = A.
3. free B → top = B (A still linked).
4. free A again → top = A, A's fd points to B — the bin is corrupted.
5. Next mallocs return A, B, then A AGAIN → overlapping chunks.
6. Overwrite A's fd to a target → dup-into-target.

## Traps

- Sizes must fit the fastbin range.
- tcache intercepts frees first on 2.26+ — exhaust the tcache size bin
  (7 frees) or the chunks never reach fastbin.

## Falsifier

glibc puts the chunk in tcache and the tcache key check fires on the
second free: plain fastbin-dup unreachable — need tcache-poison or a
key-clearing write.

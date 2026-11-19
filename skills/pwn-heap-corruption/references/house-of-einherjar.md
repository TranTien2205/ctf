# House of einherjar — null-byte consolidation


An off-by-NUL clears P and shrinks prev_size so consolidation backs into
attacker-chosen memory — overlapping a controlled region without a
heap leak.

## Steps

1. Chunk A, then B. Overflow A's last byte → B's P clears, prev_size
   becomes a small attacker-set value.
2. Plant a fake chunk at B - prev_size (inside your own data).
3. free(B) → consolidate backward to the fake chunk.
4. The merged region spans your fake chunk → the next alloc returns it.

## Needs

- An off-by-one into B's size/prev_size.
- A fake chunk whose P-bit and size satisfy the unlink checks.
- Post-2.30 unlink hardening means the fake chunk's fd/bk must be
  self-consistent.

## Falsifier

The forged prev_size can't point at a self-consistent fake chunk:
einherjar's merge rejects it.

# The last chunk standing — the tail states


A bin's last chunk has fd=0 (tcache/fastbin) or fd=&head (unsorted) —
the tail markers.

## Reading

- A mangled fd that de-mangles to 0: the tail.
- An arena pointer: mid-list.

## Falsifier

None — reading the shape.

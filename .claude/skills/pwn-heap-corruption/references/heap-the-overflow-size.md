# The overflow's size class — which chunk


An overflow's reach depends on which chunk follows: a larger neighbor
means more metadata before the next chunk — the size class decides the
forgeable fields.

## The geometry

- Overflow into a same-size neighbor: its size + first data bytes.
- Into a bigger neighbor: same, but the corruption has more runway.
- Into a bin-linked chunk: its fd/bk are in reach.

## Falsifier

The neighbor is a guard you can't touch: the overflow's reach is
fenced.

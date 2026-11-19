# Large allocations — the unsorted/large world


Services with big allocs (0x400+): unsorted and large-bin techniques
open — the unsorted leak is free, the largebin write is the goal.

## The advantage

- Big frees skip tcache entirely (size > 0x410) → unsorted directly.
- The largebin machinery is reachable.

## Falsifier

Small allocs only: the largebin is unreachable.

# Large allocations — the unsorted/large world — checklist

Companion to `heap-the-big-pool.md`.

## Checklist

- [ ] Big frees skip tcache entirely (size > 0x410) → unsorted directly.
- [ ] The largebin machinery is reachable.

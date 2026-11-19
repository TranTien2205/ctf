# binmap — the arena's occupancy bitmap


main_arena.binmap is a 128-bit bitmap of which bins hold chunks —
corrupting it makes the allocator think a bin is non-empty.

## Use

- Rarely needed — the fast paths don't consult it.
- On a miss path it decides whether the small/large walk even starts.

## Falsifier

Not a primary target — listed for completeness.

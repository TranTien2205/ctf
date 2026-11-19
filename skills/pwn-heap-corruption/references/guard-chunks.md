# Guard chunks — fencing the layout


Allocate sacrificial chunks around the corruption target so the
overflow/consolidation touches only what you choose — not the top, not
adjacent live state.

## Steps

1. alloc guard(size) — alloc victim(size) — alloc guard(size).
2. Corruption of the victim can't reach past the guards.
3. Free the guards AFTER the exploit's harvest to avoid tripping
   consolidation early.

## Falsifier

The program's alloc sizes can't create the needed guards: fencing is
partial — bound the corruption's reach instead.

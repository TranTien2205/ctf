# Time budget — the grooming cost


A heap run takes real time: the groom's frees/allocs, the leak cycle,
the verify rounds — budget accordingly.

## The estimate

- Leak: ~3-6 ops.
- Groom: ~7-15 ops.
- Corrupt+write: ~3-5 ops.
- Total: ~15-30 service interactions — script them.

## Falsifier

A one-shot service (no loop): the sequence must fit one interaction —
the grooming is the constraint.

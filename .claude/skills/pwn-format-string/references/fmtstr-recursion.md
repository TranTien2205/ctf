# Fmtstr in a recursive function


A recursive printf call: each level has its own frame and arg-offset —
the primitive exists at every level but N shifts.

## Steps

1. Each recursion level has its own arg window — N shifts.
2. If depth is controllable, pick a level and measure N there.
3. A fmtstr at depth d reads the stack from that depth's view.

## Falsifier

Depth uncontrollable and N varies unpredictably: the offset can't be
pinned.

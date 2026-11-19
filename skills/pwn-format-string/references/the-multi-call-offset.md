# The multi-call offset — when the offset shifts between calls


If the fmtstr runs in a loop or multiple call sites, the arg-offset N
may differ per call — the buffer's position in the stack varies.

## The problem

- A loop: the offset is usually stable across iterations.
- Different call sites: the offset differs per site.
- A recursive call: the offset shifts per depth.

## The fix

Measure N at the actual call site you use — don't reuse an N from a
different call.

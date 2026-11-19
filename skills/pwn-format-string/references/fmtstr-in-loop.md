# Fmtstr in a loop — repeated reads and writes


A fmtstr inside a loop (a read-print loop) re-fires every iteration: each
pass is a fresh primitive — leak in pass 1, write in pass 2.

## Steps

1. Each iteration is a fresh format call — leak and write in separate
   passes.
2. A controllable loop count = N independent primitives.
3. Stable arg-offset across iterations (same call site).

## Falsifier

The loop runs once or state doesn't persist between passes.

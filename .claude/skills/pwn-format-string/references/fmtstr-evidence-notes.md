# Evidence notes for fmtstr runs


Each fmtstr stage has a hard signal: the %p dump, the offset marker, the
changed target bytes, the redirect's effect.

## Signals

- %p reflects pointers — leak — the dump.
- marker at N — offset — 0x41414141.
- target value changed — write — the read-back.
- redirect fires — execution — output/flag.

## Falsifier

A stage's signal absent: that stage failed; don't proceed.

Record the N, the leaked values, and the target chosen — the run's
ledger.

# Partial success — when half the chain works


A chain where the leak works but the write misses: the failure is
downstream — debug the write stage, don't redo the leak.

## The discipline

Each stage's verification is independent — a broken stage doesn't
infect the others. Re-run only the failed stage.

## Falsifier

The failed stage's falsifier triggered: the whole approach changes,
not the stage's parameters.

# Detection by crash — the %s crash oracle


A %s at an unmapped address crashes — the crash IS a signal: the
specifier ran, the arg was deref'd, the addr was bad. A 1-bit read
oracle.

## The oracle

- %s at a bad addr crashes → the deref ran → the primitive exists.
- %s at a good addr doesn't → the addr valid → a 1-bit read.
- The crash signature confirms the primitive even without output.

## Steps

1. Send %s at a controlled position; a crash = the deref ran.
2. A clean return = the planted address was valid.
3. The crash-or-clean oracle reads 1 bit per attempt.

## Falsifier

No %s dereference happens regardless of the arg: the specifier isn't
reaching a pointer arg.

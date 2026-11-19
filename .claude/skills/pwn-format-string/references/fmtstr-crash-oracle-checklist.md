# The crash oracle — when output never returns — checklist

Companion to `fmtstr-crash-oracle.md`.

## Checklist

- [ ] %N$s crashes: arg N isn't a valid pointer (unmapped or not a ptr).
- [ ] %N$s survives: arg N points at mapped, NUL-terminated-ish memory.
- [ ] Iterate N: map which args are pointers — without seeing output.
- [ ] Crash/no-crash per planted candidate address: validate a guessed
- [ ] The write itself crashes: the slot is read-only (full RELRO GOT) —

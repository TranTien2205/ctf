# The crash oracle — when output never returns


No output channel: the crash becomes the signal — %N$s crashes on an
unmapped arg, survives on a mapped one — a 1-bit memory oracle.

## The probe

- %N$s crashes: arg N isn't a valid pointer (unmapped or not a ptr).
- %N$s survives: arg N points at mapped, NUL-terminated-ish memory.
- Iterate N: map which args are pointers — without seeing output.

## Turning it into exploitation

- Crash/no-crash per planted candidate address: validate a guessed
  target before the write.
- The write itself crashes: the slot is read-only (full RELRO GOT) —
  falsifier for the GOT route.

## Falsifier

The process is respawned per probe (no persistent state): the oracle
still works per-probe but state doesn't accumulate.

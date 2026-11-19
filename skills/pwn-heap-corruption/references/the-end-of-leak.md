# When the leak IS the exploit


Some challenges end at the leak: the flag sits in a readable buffer —
the whole "exploit" is the disclosure.

## Recognize it

- The flag is stored in an object — read it via UAF/stale/overlap.
- No write/exec needed — the leak channel suffices.

## Falsifier

The flag isn't memory-resident — the read gives pointers, not flags;
a write/exec ending is required.

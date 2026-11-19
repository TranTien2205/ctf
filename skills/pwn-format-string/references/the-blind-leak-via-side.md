# The blind leak via a side channel


No reflected output but the primitive runs: a %s at an address either
crashes or not — a 1-bit oracle that brute-forces a byte at a time.

## Steps

1. %s at a guessed address crashes (bad) or doesn't (valid).
2. Brute the target address byte-by-byte via the crash-or-clean.
3. A %n write's redirect IS observable — the behavior changes.
4. Look for a second channel (stderr, a log, a follow-up read) first.

## Falsifier

No oracle exists at all (the crash isn't observable either): the blind
primitive can't be read; only a blind write remains.

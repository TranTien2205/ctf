# The blind leak via a side channel — checklist

Companion to `the-blind-leak-via-side.md`.

## Checklist

- [ ] 1. %s at a guessed address crashes (bad) or doesn't (valid).
- [ ] 2. Brute the target address byte-by-byte via the crash-or-clean.
- [ ] 3. A %n write's redirect IS observable — the behavior changes.
- [ ] 4. Look for a second channel (stderr, a log, a follow-up read) first.

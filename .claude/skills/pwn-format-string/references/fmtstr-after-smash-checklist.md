# Fmtstr after a smash — when it's the second primitive — checklist

Companion to `fmtstr-after-smash.md`.

## Checklist

- [ ] 1. A smash that writes %p/%n specifiers into the buffer later printf'd:
- [ ] 2. Or the smash corrupts a pointer the printf reads.
- [ ] 3. Both primitives in one run — the smash's data IS the format.

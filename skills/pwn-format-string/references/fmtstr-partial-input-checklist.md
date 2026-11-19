# Partial input control — the fmtstr in a fixed template — checklist

Companion to `fmtstr-partial-input.md`.

## Checklist

- [ ] 1. If your bytes are concatenated into a format: the prefix's specifiers
- [ ] 2. Account for the prefix's arg consumption before yours.
- [ ] 3. The prefix may crash the call — check its bytes.

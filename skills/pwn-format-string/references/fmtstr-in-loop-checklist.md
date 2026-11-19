# Fmtstr in a loop — repeated reads and writes — checklist

Companion to `fmtstr-in-loop.md`.

## Checklist

- [ ] 1. Each iteration is a fresh format call — leak and write in separate
- [ ] 2. A controllable loop count = N independent primitives.
- [ ] 3. Stable arg-offset across iterations (same call site).

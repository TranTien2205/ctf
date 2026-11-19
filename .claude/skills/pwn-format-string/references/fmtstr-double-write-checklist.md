# The two-stage write — plant then use — checklist

Companion to `fmtstr-double-write.md`.

## Checklist

- [ ] 1. Call 1: %n into a controllable slot (e.g., a known buffer) — plant
- [ ] 2. Call 2: %N$n where arg N now reads the slot holding your planted
- [ ] 3. The classic: write the low bytes of a stack arg so it points at the

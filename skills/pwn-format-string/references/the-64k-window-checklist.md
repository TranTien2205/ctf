# The 64KB window — %hn reach — checklist

Companion to `the-64k-window.md`.

## Checklist

- [ ] target's high 6 bytes match: %hn suffices — one write.
- [ ] target differs above 64KB: need %n or %hhn sequence — more writes.
- [ ] 1. Compare the slot's current value to the target.
- [ ] 2. If only the low 2 bytes differ: one %hn writes them.
- [ ] 3. In-binary targets (non-PIE) almost always fit the 64KB window.

# The leak-depth table — which N gives which value — checklist

Companion to `the-leak-depth-table.md`.

## Checklist

- [ ] N range | Holds
- [ ] low N | your input / register args
- [ ] mid N | locals / the canary
- [ ] high N | saved regs / return addresses
- [ ] 1. Dump %p at increasing N; map each value's shape.
- [ ] 2. The canary is a word ending in 00 — find its N.
- [ ] 3. A code pointer for PIE base; a libc pointer for libc base.
- [ ] 4. The map is per-call-site — build it once, use it.

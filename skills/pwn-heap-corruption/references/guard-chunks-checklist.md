# Guard chunks — fencing the layout — checklist

Companion to `guard-chunks.md`.

## Checklist

- [ ] 1. alloc guard(size) — alloc victim(size) — alloc guard(size).
- [ ] 2. Corruption of the victim can't reach past the guards.
- [ ] 3. Free the guards AFTER the exploit's harvest to avoid tripping

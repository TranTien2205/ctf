# Fmtstr in a recursive function — checklist

Companion to `fmtstr-recursion.md`.

## Checklist

- [ ] 1. Each recursion level has its own arg window — N shifts.
- [ ] 2. If depth is controllable, pick a level and measure N there.
- [ ] 3. A fmtstr at depth d reads the stack from that depth's view.

# Exact write values — choosing what to put — checklist

Companion to `write-value-exact.md`.

## Checklist

- [ ] Redirect → gadget → chain start.
- [ ] Redirect → function → system/win directly.
- [ ] Redirect → mid-gadget → skip a prologue.
- [ ] 1. The value is the first address execution jumps to.
- [ ] 2. Under ASLR/PIE the value must be computed from the leak.
- [ ] 3. Wrong-value writes crash on redirect — verify the target exists.

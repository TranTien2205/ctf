# Truncated output — harvesting a partial leak — checklist

Companion to `fmtstr-truncated-leak.md`.

## Checklist

- [ ] 1. A capped output: the last specifiers' output is cut.
- [ ] 2. Read fewer per call: %N$p one at a time in a loop.
- [ ] 3. Or jump the window: %40$p skips the first 39 slots.
- [ ] 4. Positional args bypass the truncation — read the deep slot directly.

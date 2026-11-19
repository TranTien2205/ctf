# When the read alone suffices — no write needed — checklist

Companion to `when-read-suffices.md`.

## Checklist

- [ ] 1. If the flag is a string at a known/leaked address: plant the pointer,
- [ ] 2. If the flag's address is fixed (non-PIE .rodata), no leak needed.
- [ ] 3. Check strings/rodata for the flag first — cheapest win.

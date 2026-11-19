# When the leak IS the exploit — checklist

Companion to `the-end-of-leak.md`.

## Checklist

- [ ] The flag is stored in an object — read it via UAF/stale/overlap.
- [ ] No write/exec needed — the leak channel suffices.

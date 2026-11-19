# ROP past a canary — the leak prerequisite — checklist

Companion to `canary-rop.md`.

## Checklist

- [ ] 1. Leak the canary (a format-string read, an info disclosure).
- [ ] 2. Place the real canary value at its slot in the overflow.
- [ ] 3. The chain continues past it.

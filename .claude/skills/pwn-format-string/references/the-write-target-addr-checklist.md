# Knowing the write target's address — checklist

Companion to `the-write-target-addr.md`.

## Checklist

- [ ] 1. Choose the target (GOT slot, ret-addr, hook, global).
- [ ] 2. Get its address: static (non-PIE), base+offset (PIE), or leaked stack
- [ ] 3. Pack it as the arg-position pointer.

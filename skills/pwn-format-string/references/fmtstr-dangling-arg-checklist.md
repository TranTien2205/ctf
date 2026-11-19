# The dangling arg — reading a stale pointer — checklist

Companion to `fmtstr-dangling-arg.md`.

## Checklist

- [ ] 1. Some args are stale pointers — %s on them reads whatever's there now.
- [ ] 2. A crash — the pointer is dead.
- [ ] 3. Garbage output — the memory is valid but stale: possibly useful data.

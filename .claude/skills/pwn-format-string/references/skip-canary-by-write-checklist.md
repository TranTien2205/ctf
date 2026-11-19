# Writing around the canary via %n — checklist

Companion to `skip-canary-by-write.md`.

## Checklist

- [ ] %n → GOT slot: fires on the next call of that import.
- [ ] %n → saved return address: fires at function return; needs the stack
- [ ] %n → __free_hook: fires on next free (glibc ≤2.34).
- [ ] 1. Leak what you need (canary-free targets preferred).
- [ ] 2. Plant the target's address at a %N$n position.
- [ ] 3. Write the redirect value with the right count.

# Choosing the real target — the endgame — checklist

Companion to `the-real-target.md`.

## Checklist

- [ ] Hook exists (<=2.34) and reachable → __free_hook = system.
- [ ] Hooks gone → FILE vtable (FSOP) or an app-owned function pointer.
- [ ] Only a value-write (unsorted attack) → tcache counts or a flag word.
- [ ] Only a read → the flag buffer's address.

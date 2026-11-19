# Class boundary â€” what stack-corruption is NOT — checklist

Companion to `class-boundary.md`.

## Checklist

- [ ] Shape
- [ ] `printf(user_input)` â€” read/write via format spec
- [ ] corruption into heap chunk metadata (fd/bk, size fields)
- [ ] NX on â€” the exploit is code reuse
- [ ] a parsing crash with no write-to-saved-state

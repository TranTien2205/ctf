# pcall/xpcall wrappers — the protected call — checklist

Companion to `pcall-wrapper.md`.

## Checklist

- [ ] 1. If printf runs inside pcall: bad derefs raise internally.
- [ ] 2. The pcall's return value may propagate — check for a difference.
- [ ] 3. The %n write still works inside pcall (no error raised).

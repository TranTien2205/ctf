# Uninitialized chunk read — stale data leaks — checklist

Companion to `uninit-read.md`.

## Checklist

- [ ] 1. Free an object that held secrets (or bin pointers — a freed chunk's
- [ ] 2. Alloc same size → the chunk returns with stale bytes.
- [ ] 3. Read the "new" object's fields → the stale data leaks.
- [ ] A freed chunk's fd/bk (bin links) — heap/arena pointers.
- [ ] A previously freed object's fields — app data, keys, flags.
- [ ] tc->key fields.

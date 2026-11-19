# The flag object — targeted reuse — checklist

Companion to `the-flag-object.md`.

## Checklist

- [ ] 1. The flag is read into object F then F is freed.
- [ ] 2. Alloc same size → returns F's chunk → your object's fields overlap
- [ ] 3. show() the new object → the flag prints.

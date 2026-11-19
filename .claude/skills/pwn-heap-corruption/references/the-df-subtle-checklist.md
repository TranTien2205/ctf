# The subtle double-free — via different paths — checklist

Companion to `the-df-subtle.md`.

## Checklist

- [ ] Two slot indexes pointing at the same chunk (index confusion).
- [ ] A path alias — obj->buf vs obj itself.
- [ ] A stale pointer re-freed after re-alloc.

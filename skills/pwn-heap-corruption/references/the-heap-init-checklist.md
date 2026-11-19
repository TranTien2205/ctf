# heap init — where tcache_perthread lives — checklist

Companion to `the-heap-init.md`.

## Checklist

- [ ] The FIRST allocated chunk is the tcache struct — never a user chunk.
- [ ] All heap-base arithmetic anchors to it.

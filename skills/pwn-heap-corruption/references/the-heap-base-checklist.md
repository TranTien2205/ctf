# Naming the heap base — anchor points — checklist

Companion to `the-heap-base.md`.

## Checklist

- [ ] dm maps in r2 -d: the [heap] region's start.
- [ ] A leaked heap ptr & ~0xfff — usually within a page or two of base.
- [ ] tcache_perthread_struct at base+0x10 — a chunk's own address if it's

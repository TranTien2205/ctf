# Naming the heap base — anchor points


The heap base anchors every fake-chunk and de-mangle computation —
get it from: a heap pointer's page-alignment, a chunk's own pos, or
dm maps.

## Sources

- dm maps in r2 -d: the [heap] region's start.
- A leaked heap ptr & ~0xfff — usually within a page or two of base.
- tcache_perthread_struct at base+0x10 — a chunk's own address if it's
  the first alloc.

## Falsifier

No heap address is knowable: safe-linking aims are impossible — the
technique set narrows.

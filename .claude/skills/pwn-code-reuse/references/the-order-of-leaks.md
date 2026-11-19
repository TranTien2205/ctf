# The order of leaks — which first


1. Code/binary base (PIE) — the chain's addresses need it.
2. libc base — the libc functions/offsets need it.
3. Stack — only if a stack target is aimed.
4. Heap — only for heap-anchored fakes.

The chain can't be built until the addresses it needs are leaked.

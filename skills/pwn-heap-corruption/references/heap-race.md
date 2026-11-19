# Heap and threads — race-window corruption


A threaded service: the same object freed in one thread and used in
another — a TOCTOU UAF without an explicit bug.

## Steps

1. Thread A: free(obj) — obj enters the bin.
2. Thread B (concurrent): reads/writes obj — the use-after-free.
3. Or: A allocs, B frees mid-use — the race widens the window.

## Falsifier

The service is single-threaded or locks around alloc/free: no race
window.

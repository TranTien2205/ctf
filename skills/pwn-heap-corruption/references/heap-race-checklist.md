# Heap and threads — race-window corruption — checklist

Companion to `heap-race.md`.

## Checklist

- [ ] 1. Thread A: free(obj) — obj enters the bin.
- [ ] 2. Thread B (concurrent): reads/writes obj — the use-after-free.
- [ ] 3. Or: A allocs, B frees mid-use — the race widens the window.

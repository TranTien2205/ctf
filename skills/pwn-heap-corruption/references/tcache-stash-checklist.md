# Tcache stashing — unsorted to tcache migration — checklist

Companion to `tcache-stash.md`.

## Checklist

- [ ] 1. Corrupt an unsorted chunk's bk to a fake-chunk chain.
- [ ] 2. Trigger the sweep (malloc of a size that processes that bin).
- [ ] 3. The fake chunks land in tcache — harvest by size-matched allocs.

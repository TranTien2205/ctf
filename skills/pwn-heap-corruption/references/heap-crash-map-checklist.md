# Crash messages — reading the aborts — checklist

Companion to `heap-crash-map.md`.

## Checklist

- [ ] Abort text | Check | Bypass
- [ ] double free or corruption (fasttop) | fastbin top==victim | A-B-A order
- [ ] double free detected in tcache | e->key == tcache | overwrite key
- [ ] free(): invalid pointer | unaligned/non-heap ptr | fake a valid chunk
- [ ] free(): invalid size | size out of range | forge a sane size
- [ ] free(): invalid next size | next chunk's size bad | forge the next too
- [ ] corrupted top size | top size check | house-of-force dead
- [ ] malloc(): memory corruption | bin link inconsistency | satisfy fd/bk checks
- [ ] malloc(): smallbin double linked | fd->bk/bk->fd != chunk | self-consistent fakes
- [ ] corrupted size vs prev_size | size/prev_size mismatch | make them agree
- [ ] munmap_chunk(): invalid pointer | M-flagged fake | clear M or avoid

# The M bit — the mmap marker


M marks an mmap'd chunk — free() munmaps it, no bin interaction: the
bit diverts the whole dealloc path.

## The consequence

- A chunk wrongly M-flagged: free() munmaps it — "munmap_chunk():
  invalid pointer" aborts or a wild unmap.
- Rarely useful directly; mainly a "don't" — don't accidentally set M.

## Falsifier

The bit you meant was P — check the flag bits precisely.

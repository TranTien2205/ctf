# The calloc gate — when tcache is bypassed


calloc may bypass tcache entirely (the calloc path doesn't pull from
tcache entries in some versions) — the alloc order differs.

## The consequence

- A calloc'd object doesn't consume a tcache entry — your grooming
  count is off by one if the service callocs.
- Freed calloc'd chunks DO enter tcache normally on free.

## Falsifier

The service uses malloc only: the gate is moot.

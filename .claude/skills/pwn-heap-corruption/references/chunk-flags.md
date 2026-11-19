# N/M/P — the size-field flags


The size word's low 3 bits are flags, not size:

- P (0x01): the PREVIOUS chunk is in use — when clear, prev_size is
  live and consolidation walks back.
- M (0x02): mmap'd chunk — not heap-resident.
- N (0x04): non-main arena — belongs to a thread arena.

## Exploitation

- Clearing P (off-by-NUL) activates prev_size → consolidation eats a
  "predecessor" you forge.
- Setting N misdirects free() to a fake arena (house of mind).
- M is checked before unlink paths.

## Falsifier

The flag bit you need isn't reachable by the bug's write granularity:
the flag-level technique is closed.

# Chunk anatomy — size, flags, fd, bk


A glibc chunk carries metadata in-band: the size word (with N|M|P flag
bits), and for free chunks the fd/bk links.

## Layout

    | prev_size | size | user data ...            |
    free chunk: | prev_size | size | fd | bk | (tcache: key) |

- size low 3 bits: P (prev in use) | M (mmap'd) | N (non-main arena).
- fd points to the NEXT free chunk in the bin.
- bk points to the previous (bin-linked) chunk.
- tcache entries carry `key` after e->next for double-free detection
  (glibc >= 2.29).

## The read

r2 -d ./chal then `dmh` / `dmhf` walks the heap and prints chunk sizes,
flags and bin membership — the runtime ground truth.

## Falsifier

Corrupting user data only — if no metadata word is reachable, the bug
isn't a heap-corruption primitive.

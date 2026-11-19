# tools/pwn_cyclic.py — offset measurement driver — case catalogue

The De Bruijn pattern generator + finder: emit a pattern, send it, read the faulting 4 bytes back to the offset.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | length positional for the pattern | generate | any size |
| 2 | --find NEEDLE for the offset | 4-byte chunk or int | reads back |
| 3 | --selftest proves the pattern | offline check | run first |

## Falsifier

Falsifier — --find returns -1 for a value you THOUGHT was in the pattern: the faulting register didn't hold pattern bytes; the write didn't reach saved state.

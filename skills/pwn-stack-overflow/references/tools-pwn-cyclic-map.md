# tools/pwn_cyclic.py — offset measurement driver — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| length positional for the pattern | generate | any size |
| --find NEEDLE for the offset | 4-byte chunk or int | reads back |
| --selftest proves the pattern | offline check | run first |

## Falsifier

Falsifier — --find returns -1 for a value you THOUGHT was in the pattern: the faulting register didn't hold pattern bytes; the write didn't reach saved state.

# tools/pwn_cyclic.py — offset measurement driver

The De Bruijn pattern generator + finder: emit a pattern, send it, read the faulting 4 bytes back to the offset.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| length positional for the pattern | generate | any size |
| --find NEEDLE for the offset | 4-byte chunk or int | reads back |
| --selftest proves the pattern | offline check | run first |

## Steps

1. python3 tools/pwn_cyclic.py 300 > pattern.txt.
2. Send the pattern; read the faulting RIP's 4 pattern bytes.
3. python3 tools/pwn_cyclic.py --find <4bytes> — the offset.
4. --selftest verifies generation/lookup offline.

## Falsifier

Falsifier — --find returns -1 for a value you THOUGHT was in the pattern: the faulting register didn't hold pattern bytes; the write didn't reach saved state.

## Traps

- The needle is 4 bytes — on x64, the faulting RIP's low 4 bytes.
- Pattern works on any endian — pass the bytes as they appear in the register.

## Commands

```bash
python3 tools/pwn_cyclic.py 300
python3 tools/pwn_cyclic.py --find 0x6161616c
python3 tools/pwn_cyclic.py --selftest
```

## Cross-references

`offset-measurement.md` · `cyclic-offset.md`

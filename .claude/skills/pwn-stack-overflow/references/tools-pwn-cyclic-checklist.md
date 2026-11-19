# tools/pwn_cyclic.py — offset measurement driver — checklist

The De Bruijn pattern generator + finder: emit a pattern, send it, read the faulting 4 bytes back to the offset.

## Checklist

- [ ] python3 tools/pwn_cyclic.py 300 > pattern.txt.
- [ ] Send the pattern; read the faulting RIP's 4 pattern bytes.
- [ ] python3 tools/pwn_cyclic.py --find <4bytes> — the offset.
- [ ] --selftest verifies generation/lookup offline.

## Abort conditions

- The needle is 4 bytes — on x64, the faulting RIP's low 4 bytes.
- Pattern works on any endian — pass the bytes as they appear in the register.

## Falsifier

Falsifier — --find returns -1 for a value you THOUGHT was in the pattern: the faulting register didn't hold pattern bytes; the write didn't reach saved state.

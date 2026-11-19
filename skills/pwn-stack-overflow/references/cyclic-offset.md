# Offset measurement — the cyclic pattern

The first deliverable of every stack challenge: the exact byte offset from your input's start to the saved return address. tools/pwn_cyclic.py makes the De Bruijn pattern; a faulting register reads the offset back.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| crash with a controllable fault address | offset measurable | cyclic + fault read |
| RIP holds four pattern bytes | control proven | build the payload |
| pattern repeats but no crash at write boundary | length capped too short | not stack-smash — re-check the bound |

## Steps

1. python3 tools/pwn_cyclic.py 200 — emit a 200-byte pattern.
2. Send it as input; the process faults when the return address is a pattern chunk.
3. Read the faulting value (RIP on x64) — via r2 -d, a core dump, or the service's crash report.
4. python3 tools/pwn_cyclic.py --find <4-bytes> — the offset in the pattern.

## Falsifier

Falsifier — the faulting register never holds pattern bytes at any length: no write reaches the saved return address. Re-check the read bound; it is probably capped below the saved-state distance.

## Traps

- A crash inside the copy (segfault writing the input) is not control — you need the fault at function-return time.
- 32-bit vs 64-bit pattern: --find takes 4 bytes regardless; check the register width.
- The fault address in the log may be the pattern chunk itself, not RIP — read the right register.

## Commands

```bash
python3 tools/pwn_cyclic.py 200
python3 tools/pwn_cyclic.py --find 0x6161616c
```

## Cross-references

`control-flow.md` · `offset-measurement.md`

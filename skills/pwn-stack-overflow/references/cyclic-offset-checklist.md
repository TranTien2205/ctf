# Offset measurement — the cyclic pattern — checklist

The first deliverable of every stack challenge: the exact byte offset from your input's start to the saved return address. tools/pwn_cyclic.py makes the De Bruijn pattern; a faulting register reads the offset back.

## Checklist

- [ ] python3 tools/pwn_cyclic.py 200 — emit a 200-byte pattern.
- [ ] Send it as input; the process faults when the return address is a pattern chunk.
- [ ] Read the faulting value (RIP on x64) — via r2 -d, a core dump, or the service's crash report.
- [ ] python3 tools/pwn_cyclic.py --find <4-bytes> — the offset in the pattern.

## Abort conditions

- A crash inside the copy (segfault writing the input) is not control — you need the fault at function-return time.
- 32-bit vs 64-bit pattern: --find takes 4 bytes regardless; check the register width.
- The fault address in the log may be the pattern chunk itself, not RIP — read the right register.

## Falsifier

Falsifier — the faulting register never holds pattern bytes at any length: no write reaches the saved return address. Re-check the read bound; it is probably capped below the saved-state distance.

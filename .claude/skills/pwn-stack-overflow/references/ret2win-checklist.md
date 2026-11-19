# ret2win / ret2func — jump to a function in the binary — checklist

The simplest chain: a function in the binary does what you want (calls system, prints the flag). Overwrite the return address with its address — no libc needed.

## Checklist

- [ ] python3 tools/pwn_triage.py ./chal — check protections (PIE off = static addresses).
- [ ] r2 -A ./chal && afl — list functions; find win/flag/vuln targets.
- [ ] Measure the offset (cyclic-offset).
- [ ] Payload: pad to offset + p64(win_addr) — RIP lands on the function.

## Abort conditions

- PIE: the function's address is base+offset — need a leak of the base first.
- Call targets need the right args on the stack — ret2win with no args is the easy case.
- Stack alignment (movaps): some functions crash on misaligned RSP — pad with a ret gadget first.

## Falsifier

Falsifier — no function does what you need and the binary exposes no system-like call site: ret2win is out; go to ret2plt/ret2libc.

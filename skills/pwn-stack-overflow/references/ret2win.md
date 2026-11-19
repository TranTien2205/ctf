# ret2win / ret2func — jump to a function in the binary

The simplest chain: a function in the binary does what you want (calls system, prints the flag). Overwrite the return address with its address — no libc needed.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a function named win/flag/get_flag exists | direct call | set RIP to it |
| sym.show_flag or system call in disasm | the target exists | redirect to it |
| non-PIE binary | absolute address is stable | direct jump |

## Steps

1. python3 tools/pwn_triage.py ./chal — check protections (PIE off = static addresses).
2. r2 -A ./chal && afl — list functions; find win/flag/vuln targets.
3. Measure the offset (cyclic-offset).
4. Payload: pad to offset + p64(win_addr) — RIP lands on the function.

## Falsifier

Falsifier — no function does what you need and the binary exposes no system-like call site: ret2win is out; go to ret2plt/ret2libc.

## Traps

- PIE: the function's address is base+offset — need a leak of the base first.
- Call targets need the right args on the stack — ret2win with no args is the easy case.
- Stack alignment (movaps): some functions crash on misaligned RSP — pad with a ret gadget first.

## Commands

```bash
r2 -A ./chal && afl
r2 -A ./chal && pdf @ win
```

## Cross-references

`offset-measurement.md` · `ret2plt.md` · `rop-basics.md`

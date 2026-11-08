# Stack control flow: offset to RIP

A stack overflow finding is a chain of three measurements: the offset, the
protections, and the win path. Do them in order — a payload built before the
protections are known is a wasted crash.

## Step 1 — the offset, exactly

```bash
python3 -c "import pwn; print(pwn.cyclic(512).decode())" | ./binary
# in gdb: cyclic_find(0x6161616c) on the faulting rip/rsp value
```

`pwn.cyclic` gives a unique string per position; `cyclic_find` on the
faulting register returns the exact offset. Never guess the offset from
buffer size — stack layout adds saved-rbp, alignment, and canary slots.

## Step 2 — the protections, before any payload

```bash
checksec ./binary               # or python3 tools/pwn_triage.py ./binary
```

| Protection | Changes the plan to |
|---|---|
| no canary | classic overwrite — offset straight to ret |
| canary | leak it first (format string, read primitive) or find a path that skips the check |
| NX on | no shellcode on stack — ret2win / ret2libc / ROP |
| NX off | shellcode on stack, jmp esp or sled to it |
| PIE off | fixed addresses — ret2win or ret2plt directly |
| PIE on | need a leak first — one runtime address defeats PIE |
| Full RELRO | no GOT overwrite; partial RELRO leaves GOT writable |

## Step 3 — the win path, cheapest first

| If the binary has | The path is |
|---|---|
| a `win()`/`flag()` function | ret2win: offset + padding + `&win` |
| `system`, `puts`, `printf` in PLT + a `/bin/sh` or flag string | ret2plt with the string's address |
| libc linked, no useful gadget | ret2libc: leak libc (puts@plt -> puts@g), compute base, `system("/bin/sh")` |
| NX off, stack shellcode | jmp esp / sled |
| only a leak primitive | partial overwrite — one byte of a return address can pivot |

## The pattern that generalizes

The overflow is only the *write*; the exploit is the *layout*: offset → saved
regs → return address → chain. Every protection above answers "which of those
bytes can I trust?" — answer it before writing the payload.

## Falsifier

The crash is unreachable from input, or every reachable corruption is bounded
(canary always checked, non-writable return path) — no control of the return
address means no control-flow hijack.

## Traps

- A crash on input N is not the offset — it's where corruption *first* hits
  something critical; cyclic_find on the register, not the input length.
- 64-bit: a bad address on the stack crashes at `ret`, not at the function —
  add a `ret` gadget before the real target to fix 16-byte alignment.
- ASLR is separate from PIE — a non-PIE binary still needs a libc leak for
  ret2libc.

# x86 vs x64 argument layout — where your buffer sits — case catalogue

x86 puts all args on the stack (low N reaches your input); x64 puts the first 6 in registers (your input is at high N). The arg-offset differs fundamentally.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | ELF32 | all args on stack | low N |
| 2 | ELF64 | 6 in regs, then stack | high N |
| 3 | the buffer's N differs | the ABI decides | measure it |

## Falsifier

Falsifier — the ABI/layout assumption doesn't match the measured N: always measure; the N is per-call-site.

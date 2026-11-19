# x86 vs x64 argument layout — where your buffer sits — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| ELF32 | all args on stack | low N |
| ELF64 | 6 in regs, then stack | high N |
| the buffer's N differs | the ABI decides | measure it |

## Falsifier

Falsifier — the ABI/layout assumption doesn't match the measured N: always measure; the N is per-call-site.

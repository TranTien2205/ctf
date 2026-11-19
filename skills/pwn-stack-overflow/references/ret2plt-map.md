# ret2plt / ret2system — call an imported function — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| system in the import table | ret2system exists | one call |
| a '/bin/sh' string in .rodata or writable | arg available | rdi=string, call system |
| non-PIE or partial-RELRO | PLT address stable | direct call |

## Falsifier

Falsifier — no exec-like import and no useful PLT target: ret2plt is out; ret2libc or code-reuse chains remain.

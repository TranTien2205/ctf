# ret2plt / ret2system — call an imported function — case catalogue

system@plt, puts@plt, printf@plt: imported functions have static PLT stubs even under PIE. If the binary imports system and you control a string argument, ret2plt is the shortest chain.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | system in the import table | ret2system exists | one call |
| 2 | a '/bin/sh' string in .rodata or writable | arg available | rdi=string, call system |
| 3 | non-PIE or partial-RELRO | PLT address stable | direct call |

## Falsifier

Falsifier — no exec-like import and no useful PLT target: ret2plt is out; ret2libc or code-reuse chains remain.

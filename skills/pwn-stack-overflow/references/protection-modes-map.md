# Protections — canary, PIE, NX, RELRO, ASLR — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| CANARY present | smashing write trips __stack_chk_fail | leak it or write around it |
| PIE enabled | no absolute addresses | leak a code pointer first |
| NX on | no shellcode | code reuse — pwn-code-reuse |
| full RELRO | GOT is read-only | no GOT overwrite |
| ASLR on (default) | libc/stack addresses unknown | need a leak |

## Falsifier

Falsifier — the protections report contradicts your read of the binary: the report carries the evidence; trust the evidence, not the label.

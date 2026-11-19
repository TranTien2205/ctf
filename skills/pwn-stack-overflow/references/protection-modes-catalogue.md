# Protections — canary, PIE, NX, RELRO, ASLR — case catalogue

tools/pwn_triage.py reports each protection WITH the evidence that decided it. The sheet determines the whole chain — read it before touching a payload.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | CANARY present | smashing write trips __stack_chk_fail | leak it or write around it |
| 2 | PIE enabled | no absolute addresses | leak a code pointer first |
| 3 | NX on | no shellcode | code reuse — pwn-code-reuse |
| 4 | full RELRO | GOT is read-only | no GOT overwrite |
| 5 | ASLR on (default) | libc/stack addresses unknown | need a leak |

## Falsifier

Falsifier — the protections report contradicts your read of the binary: the report carries the evidence; trust the evidence, not the label.

# ret2shellcode — when NX is off — case catalogue

NX off means the stack (or a buffer) is executable: write your shellcode, jump to it. tools/sc_gen.py emits tested stubs — no pwntools needed.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | NX disabled in protections | shellcode executable | write + jump |
| 2 | a writable+executable region | code home | point RIP there |
| 3 | SC_GEN stubs: execve64/execve86/cat64/rev64 | tested shellcode | --raw for hex |

## Falsifier

Falsifier — NX is on: no shellcode executes regardless of control; the chain must be code-reuse.

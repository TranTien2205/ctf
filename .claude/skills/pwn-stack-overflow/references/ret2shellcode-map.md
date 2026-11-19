# ret2shellcode — when NX is off — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| NX disabled in protections | shellcode executable | write + jump |
| a writable+executable region | code home | point RIP there |
| SC_GEN stubs: execve64/execve86/cat64/rev64 | tested shellcode | --raw for hex |

## Falsifier

Falsifier — NX is on: no shellcode executes regardless of control; the chain must be code-reuse.

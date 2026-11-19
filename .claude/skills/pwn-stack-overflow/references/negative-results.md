# Negative results — recording dead routes

A closed route is a measurement with the falsifier that closed it.

## Format

Per route: what was tried, what was observed, the reopening precondition.

## The standard negatives

| Route | Negative | Reopens if |
|---|---|---|
| ret2shellcode | NX on | NX off (never in a fixed binary) |
| ret2win | no win-like function | a win function exists |
| ret2plt | no useful import | an import appears |
| ret2libc | no leak primitive | a leak surfaces |
| canary bypass | no leak, no fork | a leak or fork |
| GOT overwrite | full RELRO | partial RELRO (fixed) |
| cyclic offset | faulting reg ≠ pattern | a real write exists |
| ret2csu | no __libc_csu_init | dynamic binary |
| SROP | no syscall gadget | one appears |
| pie defeat | no leak | a leak surfaces |

## Recording

`../field-notes.md` — one line per dead route with the falsifier that
closed it. If every route is closed, record 'stack route closed: <which
falsifier>' and hand back to the router.

## Anti-pattern

A negative without the falsifier — 'exploit didn't work' records nothing.
'canary tripped at return, no leak primitive exists' records a closed
route with its reason.

# Preconditions — what must be true

| For | Must be true |
|---|---|
| the class | a write reaches saved stack state |
| ret2shellcode | NX off |
| ret2win | a winning function exists |
| ret2plt | a useful import |
| ret2libc | a leak primitive |
| canary bypass | a leak or a fork |
| GOT overwrite | partial RELRO + arb-write |
| ret2csu | __libc_csu_init present |
| SROP | syscall;ret + frame-sized stack |
| fork-brute | per-connection fork, stable canary |
| pie defeat | a leak or partial-write |

A route whose precondition is false is falsified — record it, don't build it.

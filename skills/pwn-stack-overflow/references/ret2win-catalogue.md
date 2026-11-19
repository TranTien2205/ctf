# ret2win / ret2func — jump to a function in the binary — case catalogue

The simplest chain: a function in the binary does what you want (calls system, prints the flag). Overwrite the return address with its address — no libc needed.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a function named win/flag/get_flag exists | direct call | set RIP to it |
| 2 | sym.show_flag or system call in disasm | the target exists | redirect to it |
| 3 | non-PIE binary | absolute address is stable | direct jump |

## Falsifier

Falsifier — no function does what you need and the binary exposes no system-like call site: ret2win is out; go to ret2plt/ret2libc.

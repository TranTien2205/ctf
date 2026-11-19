# ret2win / ret2func — jump to a function in the binary — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a function named win/flag/get_flag exists | direct call | set RIP to it |
| sym.show_flag or system call in disasm | the target exists | redirect to it |
| non-PIE binary | absolute address is stable | direct jump |

## Falsifier

Falsifier — no function does what you need and the binary exposes no system-like call site: ret2win is out; go to ret2plt/ret2libc.

# Fmtstr to RIP — redirecting execution — case catalogue

The write primitive's goal is execution: overwrite a return address, a GOT entry, or a hook — the next return/call/malloc goes to your chain.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a write primitive + a redirectable target | execution | the write |
| 2 | GOT / ret-addr / hook reachable | the redirect | choose it |
| 3 | the chain's first stage | a function or gadget | the target |

## Falsifier

Falsifier — no writable redirect target is reachable by the write primitive, or the redirect's arg state is wrong: no execution redirect.

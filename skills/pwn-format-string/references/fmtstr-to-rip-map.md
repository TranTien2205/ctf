# Fmtstr to RIP — redirecting execution — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a write primitive + a redirectable target | execution | the write |
| GOT / ret-addr / hook reachable | the redirect | choose it |
| the chain's first stage | a function or gadget | the target |

## Falsifier

Falsifier — no writable redirect target is reachable by the write primitive, or the redirect's arg state is wrong: no execution redirect.

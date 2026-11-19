# Leak via %p/%x — reading the stack — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| %p in a reflected output | stack dump | read the words |
| a canary-shaped word at a known depth | canary leaked | preserve it |
| a code/libc pointer shape | base leaked | compute the base |

## Falsifier

Falsifier — the output truncates the %p run or only some args are reachable: the needed depth isn't readable.

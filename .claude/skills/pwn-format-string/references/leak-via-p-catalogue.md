# Leak via %p/%x — reading the stack — case catalogue

A run of %p specifiers dumps consecutive stack words: pointers, the canary, return addresses — the leak primitive that feeds every downstream chain.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | %p in a reflected output | stack dump | read the words |
| 2 | a canary-shaped word at a known depth | canary leaked | preserve it |
| 3 | a code/libc pointer shape | base leaked | compute the base |

## Falsifier

Falsifier — the output truncates the %p run or only some args are reachable: the needed depth isn't readable.

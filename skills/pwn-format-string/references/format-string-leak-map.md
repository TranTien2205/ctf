# Format-string as a leak primitive — feeding the smash — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a %p run leaks stack words | the leak | canary/base |
| the smash needs leaked values | composition | fmtstr → smash |
| two primitives in one binary | the chain | leak then exploit |

## Falsifier

Falsifier — the leaked words don't contain the needed value, or the smash isn't exploitable anyway: the composition fails.

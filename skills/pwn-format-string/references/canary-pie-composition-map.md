# Canary + PIE leak composition — defeating both at once — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary + PIE | two leaks needed | the %p run |
| a %p at the right depths | both values | read them |
| a code pointer + a 00-ending word | base + canary | the leak |

## Falsifier

Falsifier — the %p run doesn't reach the depths where both values sit: one or both stay hidden.

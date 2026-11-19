# Canary + PIE leak composition — defeating both at once — case catalogue

PIE and a canary together need TWO leaks: a code pointer for the base AND the canary word. The fmtstr's %p run can leak both in one call.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | canary + PIE | two leaks needed | the %p run |
| 2 | a %p at the right depths | both values | read them |
| 3 | a code pointer + a 00-ending word | base + canary | the leak |

## Falsifier

Falsifier — the %p run doesn't reach the depths where both values sit: one or both stay hidden.

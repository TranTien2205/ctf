# Format-string as a leak primitive — feeding the smash — case catalogue

A format-string read isn't always the exploit — often it's the LEAK that feeds a stack-overflow chain: the canary, the PIE base, a libc pointer.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a %p run leaks stack words | the leak | canary/base |
| 2 | the smash needs leaked values | composition | fmtstr → smash |
| 3 | two primitives in one binary | the chain | leak then exploit |

## Falsifier

Falsifier — the leaked words don't contain the needed value, or the smash isn't exploitable anyway: the composition fails.

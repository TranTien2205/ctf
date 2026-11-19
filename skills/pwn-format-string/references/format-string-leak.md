# Format-string as a leak primitive — feeding the smash

A format-string read isn't always the exploit — often it's the LEAK that feeds a stack-overflow chain: the canary, the PIE base, a libc pointer.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a %p run leaks stack words | the leak | canary/base |
| the smash needs leaked values | composition | fmtstr → smash |
| two primitives in one binary | the chain | leak then exploit |

## Steps

1. Trigger the format read; dump the %p words.
2. Extract the canary (00-ending word), the code pointer (PIE base), or the libc pointer.
3. Feed the leaked values into the stack-overflow payload.
4. The fmtstr is the leak; the smash is the exploit.

## Falsifier

Falsifier — the leaked words don't contain the needed value, or the smash isn't exploitable anyway: the composition fails.

## Traps

- The same fmtstr primitive that reads also writes — decide which you need.
- The leak is valid for the process instance — re-leak per exec.

## Cross-references

`canary-pie-composition.md` · `../pwn-stack-overflow/`

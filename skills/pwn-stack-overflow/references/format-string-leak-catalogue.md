# Format string as a leak primitive — case catalogue

A format-string read (%p, %s, %x) dumps stack/registers — the leak primitive that feeds canary and PLE leaks. Ownership is pwn-format-string's class; this file is the bridge.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | printf(user_input) or similar | format leak exists | %p leak |
| 2 | a %p that shows stack words | canary/pointer leak | read the right depth |

## Falsifier

Falsifier — the format-string isn't controllable to the needed depth, or the target value isn't on the stack: no leak via this path.

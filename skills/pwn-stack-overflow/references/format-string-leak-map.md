# Format string as a leak primitive — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| printf(user_input) or similar | format leak exists | %p leak |
| a %p that shows stack words | canary/pointer leak | read the right depth |

## Falsifier

Falsifier — the format-string isn't controllable to the needed depth, or the target value isn't on the stack: no leak via this path.

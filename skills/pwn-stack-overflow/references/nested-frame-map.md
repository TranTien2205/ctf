# Nested frames — the overflow inside a called function — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the read is in a helper called by main | two returns available | chain them |
| helper returns then main returns | nested control | chain across frames |
| one smash, two return addresses | double redirect | the layout |

## Falsifier

Falsifier — only the helper's return is reachable and the useful redirect needs main's frame: the second return is unreachable.

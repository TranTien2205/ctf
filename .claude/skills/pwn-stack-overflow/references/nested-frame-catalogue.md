# Nested frames — the overflow inside a called function — case catalogue

The vulnerable read often sits inside a helper function called by main: the smash controls the HELPER's return first, then main's — a chain across frames.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the read is in a helper called by main | two returns available | chain them |
| 2 | helper returns then main returns | nested control | chain across frames |
| 3 | one smash, two return addresses | double redirect | the layout |

## Falsifier

Falsifier — only the helper's return is reachable and the useful redirect needs main's frame: the second return is unreachable.

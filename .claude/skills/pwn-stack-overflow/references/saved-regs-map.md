# Saved registers — the frame layout — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| saved RIP holds your bytes | return control | p64(target) |
| saved RBP corrupted | frame chain | leave;ret pivot |

## Falsifier

Falsifier — the write stops before the saved registers: the bound is too short; check the read's bound.

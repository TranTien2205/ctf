# Saved registers — the frame layout — case catalogue

The stack frame: [locals][canary?][saved RBP][saved RIP][args]. Smashing past saved RBP hits saved RIP — the offset math lives here.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | saved RIP holds your bytes | return control | p64(target) |
| 2 | saved RBP corrupted | frame chain | leave;ret pivot |

## Falsifier

Falsifier — the write stops before the saved registers: the bound is too short; check the read's bound.

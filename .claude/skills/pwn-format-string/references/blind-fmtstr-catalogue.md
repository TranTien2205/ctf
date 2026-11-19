# Blind format string — no reflected output — case catalogue

Sometimes the printf output isn't returned to you: the primitive exists but you can't see the leak. Blind techniques read via a side channel or write blindly.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the format executes but output isn't shown | blind | side-channel read |
| 2 | a %s read can trigger a crash on bad addr | crash oracle | read via crash |
| 3 | a write still works blind | %n without feedback | the write |

## Falsifier

Falsifier — no output channel and no usable side-channel oracle: the read primitive can't be harvested; only a blind write remains.

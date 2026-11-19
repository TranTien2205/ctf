# Blind format string — no reflected output — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the format executes but output isn't shown | blind | side-channel read |
| a %s read can trigger a crash on bad addr | crash oracle | read via crash |
| a write still works blind | %n without feedback | the write |

## Falsifier

Falsifier — no output channel and no usable side-channel oracle: the read primitive can't be harvested; only a blind write remains.

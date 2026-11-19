# The argument-offset finder — where your buffer lands — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a %p leak shows your bytes | the offset is findable | scan N |
| you plant a pointer for %s/%n | need its argument index | the offset |
| x64 first args in regs | N ≥ ~6 for the stack | the stack args |

## Falsifier

Falsifier — your input never appears as a %N$p value at any N: the buffer isn't a printf argument; the primitive can't reach it.

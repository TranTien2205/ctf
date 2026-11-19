# The argument-offset finder — where your buffer lands — case catalogue

Every %N$p or %N$n needs the offset N where YOUR input sits as a printf argument. AAAA.%N$p scanning N until 0x41414141 returns is the measurement.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a %p leak shows your bytes | the offset is findable | scan N |
| 2 | you plant a pointer for %s/%n | need its argument index | the offset |
| 3 | x64 first args in regs | N ≥ ~6 for the stack | the stack args |

## Falsifier

Falsifier — your input never appears as a %N$p value at any N: the buffer isn't a printf argument; the primitive can't reach it.

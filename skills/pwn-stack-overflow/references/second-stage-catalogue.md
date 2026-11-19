# Two-stage exploits — leak first, then exploit — case catalogue

Many chains need two rounds: first a leak (canary, libc base, stack address), then the real payload built with the leaked values.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | need a leaked value in the payload | two-stage | leak then re-trigger |
| 2 | the service loops after the leak | re-triggerable | send stage 2 |
| 3 | one-shot only | can't re-trigger | single-shot chain or fork-brute |

## Falsifier

Falsifier — the service doesn't re-trigger and the chain needs two stages: single-shot is required — combine the leak and the smash in one input if the protocol allows.

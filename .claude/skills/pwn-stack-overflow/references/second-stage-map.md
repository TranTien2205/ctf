# Two-stage exploits — leak first, then exploit — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| need a leaked value in the payload | two-stage | leak then re-trigger |
| the service loops after the leak | re-triggerable | send stage 2 |
| one-shot only | can't re-trigger | single-shot chain or fork-brute |

## Falsifier

Falsifier — the service doesn't re-trigger and the chain needs two stages: single-shot is required — combine the leak and the smash in one input if the protocol allows.

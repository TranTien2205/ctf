# Leak-then-use — composing the two primitives — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a leak primitive exists | the values | canary/base |
| the smash needs leaked values | composition | leak → build → send |
| re-triggerable service | two stages | leak then smash |

## Falsifier

Falsifier — the service can't re-trigger and the primitives can't compose in one input: the two-stage is impossible; need a leak-free chain.

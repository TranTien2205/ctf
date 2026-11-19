# Leak-then-use — composing the two primitives — case catalogue

The standard hard-case chain: an info-leak primitive (format-string, uninit read) feeds values into the stack-smash payload — leak first, exploit second.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a leak primitive exists | the values | canary/base |
| 2 | the smash needs leaked values | composition | leak → build → send |
| 3 | re-triggerable service | two stages | leak then smash |

## Falsifier

Falsifier — the service can't re-trigger and the primitives can't compose in one input: the two-stage is impossible; need a leak-free chain.

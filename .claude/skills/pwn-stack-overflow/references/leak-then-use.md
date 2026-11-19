# Leak-then-use — composing the two primitives

The standard hard-case chain: an info-leak primitive (format-string, uninit read) feeds values into the stack-smash payload — leak first, exploit second.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a leak primitive exists | the values | canary/base |
| the smash needs leaked values | composition | leak → build → send |
| re-triggerable service | two stages | leak then smash |

## Steps

1. Stage 1: trigger the leak; read the canary/base/pointer from the response.
2. Stage 2: trigger the overflow; build the payload with the leaked values.
3. A looping/forking service re-triggers cleanly.
4. A one-shot service must compose both in one input.

## Falsifier

Falsifier — the service can't re-trigger and the primitives can't compose in one input: the two-stage is impossible; need a leak-free chain.

## Traps

- The leaked value is valid only for that process instance.
- Fork-per-connection: same canary; exec-per-connection: re-leak each time.
- Compose in one input if the protocol allows a format read inside the smash.

## Cross-references

`second-stage.md` · `one-shot-constraints.md`

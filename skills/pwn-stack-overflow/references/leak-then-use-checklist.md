# Leak-then-use — composing the two primitives — checklist

The standard hard-case chain: an info-leak primitive (format-string, uninit read) feeds values into the stack-smash payload — leak first, exploit second.

## Checklist

- [ ] Stage 1: trigger the leak; read the canary/base/pointer from the response.
- [ ] Stage 2: trigger the overflow; build the payload with the leaked values.
- [ ] A looping/forking service re-triggers cleanly.
- [ ] A one-shot service must compose both in one input.

## Abort conditions

- The leaked value is valid only for that process instance.
- Fork-per-connection: same canary; exec-per-connection: re-leak each time.
- Compose in one input if the protocol allows a format read inside the smash.

## Falsifier

Falsifier — the service can't re-trigger and the primitives can't compose in one input: the two-stage is impossible; need a leak-free chain.

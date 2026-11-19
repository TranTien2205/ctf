# Negative results — what to record when the answer is no — checklist

A negative is a measurement with a falsifier attached. Recording it stops
the next pass (or the next agent) from re-proving it.

## Checklist

- [ ] check: ECB
- [ ] check: Padding oracle
- [ ] check: Nonce reuse
- [ ] check: Length extension
- [ ] check: Bit-flip
- [ ] check: Timing oracle
- [ ] check: Key path

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.

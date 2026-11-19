# Argument index math — computing N


The arg index N = (bytes from varargs-start to your input) / wordsize +
register_args. Measure it, but knowing the math validates the measurement.

## The math

- On x64: N ≈ 6 + (offset_from_stack_args / 8).
- The input's stack position relative to the arg area decides N.
- Measure it; the math is the sanity check.

## Falsifier

Computed N ≠ measured N: trust the measurement; the math is approximate.

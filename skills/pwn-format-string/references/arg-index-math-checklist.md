# Argument index math — computing N — checklist

Companion to `arg-index-math.md`.

## Checklist

- [ ] On x64: N ≈ 6 + (offset_from_stack_args / 8).
- [ ] The input's stack position relative to the arg area decides N.
- [ ] Measure it; the math is the sanity check.

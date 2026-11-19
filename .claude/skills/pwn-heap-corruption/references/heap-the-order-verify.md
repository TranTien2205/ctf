# Verifying order assumptions — first-fit


"Last freed is next returned" holds ONLY within the same bin — cross-
bin, the first-fit walk decides. Verify the actual return order.

## The check

    free A; free B; alloc → which address returns?

The observed order is the ground truth — not the model.

## Falsifier

The order differs from the model: re-derive the bin routing for that
size class.

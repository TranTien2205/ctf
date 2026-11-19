# Exact write values — choosing what to put


The value written to the redirect slot is the chain's first address: a
gadget, a function, or a libc target.

## Shapes

- Redirect → gadget → chain start.
- Redirect → function → system/win directly.
- Redirect → mid-gadget → skip a prologue.

## Steps

1. The value is the first address execution jumps to.
2. Under ASLR/PIE the value must be computed from the leak.
3. Wrong-value writes crash on redirect — verify the target exists.

## Falsifier

The needed value isn't derivable (no leak for an ASLR'd target): the
write is blind → pick a deterministic target.

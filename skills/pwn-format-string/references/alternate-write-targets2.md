# More write targets — the stack data itself


Beyond redirect slots, %n can patch DATA on the stack: a length field,
a bounds check variable, an index — flipping a check is sometimes the
win.

## Shapes

- A bounds var on the stack → patch the bound.
- A loop counter/flag on stack → patch control flow.
- A vtable pointer → virtual-call redirect.

## Steps

1. Stack locals are at leakable addresses — %n to a length/index/bounds
   var.
2. A patched bound lets a later bounded-read overflow.
3. A patched flag/enum flips a check.

## Falsifier

No useful writable local sits at a known stack address.

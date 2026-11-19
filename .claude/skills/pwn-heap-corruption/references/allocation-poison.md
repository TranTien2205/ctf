# Allocation poisoning — what the next alloc sees


After corruption, the NEXT alloc of that size is the harvest — its
return value and its content decide whether the poison worked.

## The check

- The alloc's return = your target → aim confirmed.
- The alloc's content = the target's bytes → a read primitive.
- A write into it = the payload landing.

## Falsifier

The harvest returns a different chunk (the bin state wasn't what the
recipe assumed): re-derive the bin order from dmh.

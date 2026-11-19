# The unbounded read — the full-control case


When the read has no bound (a gets/scanf/%s/read(-1)): the overflow's
size is unlimited — the chain can be any length.

## The advantage

- No pivot needed — the full chain fits.
- The canary is the only gate.

## Falsifier

A bound exists: the chain must fit — the pivot/second-stage recipes.

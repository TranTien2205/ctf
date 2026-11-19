# Partial input control — the fmtstr in a fixed template


Your input may be embedded in a larger format: printf("%s", buf) is
CLOSED, but printf(buf) where buf = "prefix" + yours is open — the
prefix shifts your offset.

## Steps

1. If your bytes are concatenated into a format: the prefix's specifiers
   run first.
2. Account for the prefix's arg consumption before yours.
3. The prefix may crash the call — check its bytes.

## Falsifier

The prefix contains specifiers that consume past your data or crash:
the primitive order changes.

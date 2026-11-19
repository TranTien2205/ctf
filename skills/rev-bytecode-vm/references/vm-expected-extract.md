# Extracting expected values

The cmp's right operand is the expected constant — a pushed immediate or a const-pool entry; extract per byte.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

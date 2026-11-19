# Negative: unreadable marshal

The .pyc's version had no reader — needed xdis; don't misread garbage constants.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

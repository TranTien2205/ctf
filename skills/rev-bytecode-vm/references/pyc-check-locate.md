# Locating the check in a .pyc

--strings for names (check/verify) + flag-shaped consts → dis only that code object → find the COMPARE_OP → read its operands.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

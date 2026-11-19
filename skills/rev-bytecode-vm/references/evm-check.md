# The EVM contract check

PUSH/DUP/EQ/ISZERO/JUMPI — the deciding JUMPI after the compare; PUSH constants hold expected bytes.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

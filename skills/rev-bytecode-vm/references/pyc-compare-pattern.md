# The COMPARE_OP pattern

COMPARE_OP argval names the op (==/!=/in/is) — the loads feeding it are the transformed input and the expected; the POP_JUMP after it is the decision.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

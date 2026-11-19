# The deciding instruction

COMPARE_OP / i32.eq / JUMPI / the VM's cmp — the instruction that splits the verdict.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

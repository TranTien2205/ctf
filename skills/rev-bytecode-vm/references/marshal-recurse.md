# The marshal recursion

Nested code objects in co_consts — recurse: every function/lambda/class is a separate code object to dis.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

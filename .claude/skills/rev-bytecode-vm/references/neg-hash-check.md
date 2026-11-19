# Negative: the digest check

A SHA/digest cmp can't be inverted — the flag isn't in the bytecode's constants.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

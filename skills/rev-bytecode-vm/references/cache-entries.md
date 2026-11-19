# Inline caches

3.11+ inline cache entries appear as CACHE ops — skip them; they're not real instructions.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

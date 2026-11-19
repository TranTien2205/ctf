# The fail-fast oracle

A checker exiting at the first wrong byte is a position oracle — brute each byte by where it fails.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

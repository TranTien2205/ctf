# Decoding the program stream

The prog[] byte array decodes against the table — pc walks ops + immediates; a flag-checker is a read-transform-cmp chain.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

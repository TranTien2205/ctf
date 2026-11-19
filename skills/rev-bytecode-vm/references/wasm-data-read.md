# WASM data segment read

Expected bytes in a data segment — i32.load8_u reads memory at an offset; dump the segment bytes.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

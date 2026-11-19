# WASM stack ops

local.get/i32.const/i32.xor/i32.eq/br_if — the check is a typed stack sequence; the transform is the op chain.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

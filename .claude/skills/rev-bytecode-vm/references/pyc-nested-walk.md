# Walking nested code objects

Module code's co_consts nests function/class/lambda code objects — the check lives in one of them. Recurse: `for c in co_consts: if hasattr(c,'co_code'): dis.dis(c)`.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

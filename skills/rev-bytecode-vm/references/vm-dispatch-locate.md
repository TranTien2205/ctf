# Locating the dispatch loop

The loop: read opcode, index handlers, execute — in disasm it's an indexed load in a loop feeding a switch or indirect jump. `r2 -A; pdf @ vm_run`.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

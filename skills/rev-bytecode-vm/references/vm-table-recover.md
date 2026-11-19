# Recovering the opcode table

Read EVERY case/handler — name each op (push/pop/add/xor/read/cmp/jmp/win). The table IS the ISA.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

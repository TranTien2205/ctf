# javap on a .class

javap -c -p disassembles — constant pool + per-method bytecode; if_icmp/iflcmp jumps are the compares.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.

# IL op: ldc.i4.s

The CIL opcode `ldc.i4.s` — one instruction in the managed stack machine; read it inside the check's method body as part of the transform or the control flow.

## In the check

Appears in the IL sequence between the input load and the deciding compare — its role (load/store/arith/branch) is read in context.

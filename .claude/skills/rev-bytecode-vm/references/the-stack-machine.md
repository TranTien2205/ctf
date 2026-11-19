# The stack machine — how bytecode computes


CPython is a stack machine: LOAD pushes, BINARY_OP pops2+pushes1,
STORE pops to a name, CALL pops args+callable, RETURN pops the value.

## The trace

Track the stack depth mentally: each op's push/pop — the check's
logic is the stack's evolution.

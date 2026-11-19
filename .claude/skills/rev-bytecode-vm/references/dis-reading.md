# Reading dis output — the column guide

dis.dis output columns:

    OFFSET  OPNAME            ARG   ARGVAL
        0   LOAD_CONST            1 (b'flag{')
        2   LOAD_FAST             0 (x)
        4   BINARY_OP             0 (+)

## The reading pattern

- LOAD_* pushes a value — the argval shows what.
- BINARY_OP/UNARY_* does the math — the transform.
- STORE_* names a value.
- COMPARE_OP pops 2, pushes the result — the check.
- POP_JUMP_IF_* branches on it — the decision.
- CALL_FUNCTION/CALL calls — the helper.
- RETURN_VALUE returns the top.

## Following the check

Find the COMPARE_OP, read back the LOADs feeding it — the left is
the transformed input, the right is the expected.

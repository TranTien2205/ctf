# The check in bytecode — the pattern


The check compiles to: LOAD input, LOAD expected, COMPARE_OP, JUMP —
the bytecode's COMPARE_OP is the deciding instruction.

# The dis walk — reading the bytecode


dis.dis output: offset, opname, arg, argval — the stack-machine
program. Read it as: loads (LOAD_*), ops (BINARY_*/UNARY_*), stores
(STORE_*), control (POP_JUMP_*/JUMP_*), calls (CALL_*/RETURN).

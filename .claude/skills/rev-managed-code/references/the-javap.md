# javap — the JDK's disassembler

`javap -c -p Main` — the always-available floor when a JDK exists:
the constant pool + per-method bytecode.

## The check pattern

    aload_0              ; input
    ldc "expected"       ; a constant
    invokevirtual String.equals
    ifeq fail            ; the deciding branch

The ldc operand resolves through the constant pool.

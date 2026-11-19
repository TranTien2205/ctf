# The custom VM — the dispatch loop


A custom VM: a fetch-decode-execute loop with an opcode table —
recover the TABLE before reading one instruction of its program.

## The shape

    while True:
        op = bytecode[pc++]
        dispatch[op](...)

The dispatch table (a dict/array of handlers) maps opcodes to
operations.

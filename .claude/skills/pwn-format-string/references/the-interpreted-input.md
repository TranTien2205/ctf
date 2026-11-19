# The input AS the program — the interpreter model


The format string is a program and printf is its interpreter: the
specifiers are opcodes, the args are operands. Exploitation is writing a
program in this tiny language.

## The opcodes

- %p/%x = READ arg.
- %s = DEREF arg.
- %n/%hn/%hhn = WRITE *arg.
- %N$... = indexed addressing.
- The count = the program's accumulator.

## Falsifier

Your input isn't the format argument: the interpreter runs a different
program.

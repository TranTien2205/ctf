# Evidence — what a bytecode solve looks like — checklist

Companion to `evidence-depth.md`.

## Checklist

- [ ] The disassembly quoting the deciding compare (COMPARE_OP, JUMPI,
- [ ] The decoded program / the recovered opcode table.
- [ ] The produced input accepted by the interpreter.
- [ ] The flag through hooks.py pre-flag.
- [ ] A disassembly dump never analyzed.
- [ ] An opcode table never applied to a program.
- [ ] A flag-shaped constant never verified as the accepted input.
- [ ] "The VM checks X" without a decoded program.

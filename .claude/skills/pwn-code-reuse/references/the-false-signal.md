# False signals — the traps


- A `pop rdi` that isn't: the disassembly's byte-alignment — verify
  the tail ends in ret.
- A leak value that ISN'T a pointer: read the wrong field.
- A win function that prints a decoy: disassemble before chaining.
- A clean exit: not success — the observable must fire.

# The dispatch loop — the VM's heart


The loop reads an opcode, looks it up, executes a handler — recover
the opcode→handler mapping first; then the program's instruction
stream decodes.

# Entering mid-instruction — the byte-level gadget


Gadgets can start inside other instructions — a `ret` byte (0xc3)
inside a larger instruction is a valid ret gadget; /R finds them.

## The caution

The address shown is where execution must land — a mid-instruction
gadget's tail may differ from the source instruction's intent.

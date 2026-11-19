# Why code reuse works — the theory


NX removes code injection; the binary's own instructions remain
executable — a ret-terminated sequence is a "program" whose opcodes
are gadget addresses and whose data is the argument values. The stack
pointer is the instruction pointer; each ret consumes the next
instruction. The chain is a bytecode program interpreted by ret.

## The three constraints

- Gadget availability — what instructions exist.
- Register control — what args can be set.
- Address knowledge — what the base + leaks give.

The exploit is the intersection.

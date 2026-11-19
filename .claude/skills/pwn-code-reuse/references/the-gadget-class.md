# Gadget classes — the vocabulary


| Gadget | Shape | Use |
|---|---|---|
| pop | pop rX; ret | set a register |
| mov-store | mov [rX], rY; ret | arbitrary write |
| mov-load | mov rX, [rY]; ret | arbitrary read |
| xor | xor rX, rX; ret | zero a register |
| call/jmp | call func / jmp reg | transfer |
| syscall | syscall; (ret) | kernel call |
| pivot | leave; ret / xchg rsp | move the stack |
| ret | ret | alignment |

The chain composes these primitives.

# The write primitive — the mov-store gadget


`mov [rX], rY; ret` writes rY at [rX] — the arbitrary write; combine
with pops to aim it.

## The recipe

    pop rdi ; the_address
    pop rsi ; the_value
    mov [rdi], rsi ; ret

## The variants

- `mov [rax], rcx`, `mov [rdi], rax` — any register pair works.
- On x86 the same shape with dword regs.

## Falsifier

No store-shaped gadget exists: the write needs a different mechanism
(syscall write to memory doesn't exist — a planted-string via read()
or a different route).

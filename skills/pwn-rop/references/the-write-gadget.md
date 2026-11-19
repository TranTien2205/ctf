# The write gadget — composing a store


`mov [rdi], rsi; ret`-shaped: pop the address and the value, the mov
writes — the arbitrary-write primitive.

    pop rdi ; target_addr
    pop rsi ; value
    mov [rdi], rsi ; ret

## The uses

- Plant /bin/sh in .bss.
- Overwrite a GOT entry (partial RELRO).
- Stage a second chain in a known buffer.

# The second stage — read() into a bigger buffer


When the first chain only gets a read primitive: use it to pull a
bigger second-stage chain into memory.

## The recipe

    pop rdi ; 0        # stdin
    pop rsi ; writable_addr
    pop rdx ; len
    read@plt / read syscall
    # then pivot into writable_addr

## Falsifier

No read primitive and no writable region: the second stage can't land.

# Leaking through the GOT — puts(puts@got)


The classic leak: call a print function on a GOT entry's own address —
the resolved libc pointer prints; subtract the symbol offset → libc base.

## The recipe

    pop rdi ; puts@got
    puts@plt

The printed bytes = the resolved puts address — leak it, compute
libc_base = leaked - puts_offset.

## The restart

After the leak, the chain continues (another ret into main or the
vulnerable function) to land the real payload — a two-stage exploit.

## Falsifier

No print-capable function in the PLT (puts/printf/write): the leak
needs a different channel — a write gadget to a known socket/fd, or a
crash-based disclosure.

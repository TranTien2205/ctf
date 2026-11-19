# Write-what-where — the arbitrary write chain


Need to write a value at an address: find a `mov [rX], rY` gadget —
set rX = the address, rY = the value — the write primitive.

## The gadgets

- `mov [rdi], rsi; ret` — write rsi at [rdi].
- `mov [rax], rdx; ret` — variants by register.
- `pop rdi ; ptr` + `pop rsi ; val` + `mov [rdi], rsi ; ret`.

## The planted-string use

Writing "/bin/sh" into .data when no "/bin/sh" exists in the binary —
the write sets up the later system call's argument.

## Falsifier

No `mov [rX], rY`-shaped gadget exists: the arbitrary write can't be
expressed — use a syscall-based write (read() into a buffer) or a
different mechanism.

# The PLT targets — what's callable


afl / nm lists the PLT entries — the callable imports:

- puts/printf/write — the leak channel.
- read/gets/scanf — the second-stage channel.
- system/execve — the ending (rarely present directly).
- malloc/free/mmap — heap/sys primitives.
- exit — the clean ending.

Every needed action should map to a PLT entry or a gadget.

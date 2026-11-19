# Checking the imports — the call surface


What's PLT-callable decides the leak and stage-2 channels:

- puts/printf/write — the printer.
- read/gets/fgets — the stager.
- system/execve — the shortcut ending.
- mprotect — the page flip.
- exit — the clean end.

## The command

    nm -D ./chal
    python3 tools/elf_info.py ./chal

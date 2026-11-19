# Planting the string — the /bin/sh write


When no "/bin/sh" exists in memory, write it: a write gadget, or a
read() into a known buffer, plants the string the call needs.

## The recipes

1. write gadget: mov [rdi], rsi — write "/bin/sh\x00" as a qword.
2. read into .bss: the string arrives via stdin.
3. Existing data: a "sh" substring in the binary (`strings -a`).

## Falsifier

No way to plant and no existing string: the call can't get its arg —
an execve-by-shellcode or a different ending.

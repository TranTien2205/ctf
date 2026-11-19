# The imported functions — the PLT inventory


Each import is a PLT-callable — the list is the call surface:

    nm -D ./chal
    r2 -A ./chal ; iif

## The common ones and their uses

- puts/printf: the leak printer.
- read/gets: the stage-2 input.
- system/execve: the ending.
- mprotect: the page-flip.
- exit: the clean ending.

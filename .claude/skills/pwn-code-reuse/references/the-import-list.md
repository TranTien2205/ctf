# The import list — what the PLT offers


nm -D ./chal or r2 -A + iif lists the imports — the PLT's call surface.

## The useful ones

- puts/printf/write — leak channels.
- read/gets/fgets/scanf — input channels (stage 2, plant).
- system/execve — endings (when imported).
- mprotect — the page-flip.
- exit — the clean ending.

## Falsifier

The needed function isn't imported: reach it via libc (with a leak)
or compose it from gadgets.

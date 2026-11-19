# The two-stage chain — leak then execute


The standard dynamic-binary shape:

- Stage 1: leak a GOT entry via puts@plt(puts@got); ret to main.
- Stage 2: with libc base known, the real chain — system("/bin/sh").

## The restart

Stage 1's last entry is a return to the vulnerable path — the program
loops, and stage 2's chain runs on the now-known addresses.

## Falsifier

No re-entry: single-stage — leak must already exist or the chain must
be leak-free.

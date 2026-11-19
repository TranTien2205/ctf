# The PLT is enough — no-libc chains


A chain of ONLY PLT calls (read/write/mprotect + your binary's funcs)
runs without any libc leak — every needed primitive already imported.

## The shape

    read@plt → a bigger buffer → mprotect@plt → the planted code

Or: puts@plt for the leak → restart → the real call.

## Falsifier

The needed function isn't imported: the chain must reach libc — the
leak is required.

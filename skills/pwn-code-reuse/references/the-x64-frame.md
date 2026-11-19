# The x64 frame — the standard layout


The overflow's layout on x64:

    [buffer bytes ............]
    [saved rbp (8)]
    [saved rip ← the overwrite]
    [gadget 1]
    [arg]
    [gadget 2]
    ...

Each slot is 8 bytes; the chain is contiguous.

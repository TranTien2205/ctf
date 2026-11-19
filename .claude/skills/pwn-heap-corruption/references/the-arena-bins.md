# bins[] inside the arena — the unsorted head


main_arena.bins[] holds the bin heads; the unsorted bin's head entry is
the address the first big free writes into its fd/bk — the leak's
source value.

## The leak math

    fd = &main_arena.bins[unsorted] - 0x10 (x64, roughly)
    libc_base = leaked_fd - offset_in_libc

The offset is version/build-specific — compute from the shipped libc.

## Falsifier

No chunk reaches unsorted (all frees eaten by tcache/fastbin): the
leak needs a bin the size reaches — exhaust tcache first.

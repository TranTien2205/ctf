# Reading the GOT — the resolved pointers


GOT entries after first-call hold resolved libc addresses — reading
them via puts(got[x]) or a print leaks libc.

## The math

    libc_base = *(got[x]) - x's_libc_offset

The offset is per-libc — identify the version first.

## Falsifier

The function wasn't called yet (lazy binding — GOT holds the resolver
stub, not a libc address): call it once first, or read a different
(already-resolved) entry.

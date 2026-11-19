# Breakpoint strategy — where to pause


Break BEFORE and AFTER the corruption, and inside the allocator on the
consuming op — the diff between states is the ground truth.

## The set

- Before the corrupting op (the overflow/UAF write): `db <addr>`.
- Inside _int_free after your free: watch the bin link happen.
- Inside _int_malloc on the harvest alloc: watch the return.
- On __libc_abort/glibc's error path: catch which check fired.

## Commands

    r2 -d ./chal
    db sym.imp.free
    dc
    dmh ; dmhf      # heap + bins after each op

# read(0,...) — stdin as the second stage


read from fd 0 (stdin) into a writable page, then pivot — the
canonical second-stage when the overflow is too small.

## The chain

    pop rdi ; 0
    pop rsi ; writable_addr
    pop rdx ; big_len
    read@plt (or syscall read)
    # send the real chain; then pivot to writable_addr

## Falsifier

No read reachable or no writable page: the second-stage route closes.

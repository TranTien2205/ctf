# xchg rsp — the register pivot


`xchg rsp, rax; ret` (or similar): rsp and rax swap — if rax holds a
buffer address, rsp becomes it.

## Falsifier

rax isn't the buffer address at the pivot point: the xchg goes the
wrong way.

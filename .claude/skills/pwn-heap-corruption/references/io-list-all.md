# _IO_list_all — the FILE chain head


_IO_list_all heads the linked list of open FILEs — corrupting it and
forcing a flush walk (_IO_flush_all_lockp on exit/abort) walks YOUR
chain — the FSOP arbiter.

## The recipe

1. Write _IO_list_all = your fake FILE chain head.
2. Each fake FILE needs _chain → next fake; last → 0.
3. On exit()/abort, flush-all calls each FILE's vtable _IO_overflow —
   your skewed vtable entries fire.

## Falsifier

The write can't reach _IO_list_all or no flush path runs after:
_list_all pivot is closed.

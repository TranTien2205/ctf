# The FILE vtable — the FSOP target


A FILE's _vtable pointer decides its function table — forge it, and
the next FILE op (printf's vfprintf, a close) calls your function.

## The checks

_IO_validate_vtable bounds the table to __libc_IO_vtables on modern
glibc — forge within bounds or use a checked-entry's trick.

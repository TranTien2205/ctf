# _IO_vtable_check — the FSOP gauntlet


Since 2.24, stdio calls verify the vtable pointer is inside
__libc_IO_vtables — a forged vtable must point into that region.

## The workarounds

- Use a REAL vtable's address, offset to a different entry — the
  "vtable skew": point at _IO_str_jumps - delta so entry N calls your
  target.
- _IO_wfile_jumps and friends are inside the section — entries' call
  signatures differ, choose one whose args your controllable fields
  satisfy.

## Falsifier

No valid in-section vtable maps your needed call to a useful function
pointer: FSOP vtable-skew fails — use _IO_list_all or hooks instead.

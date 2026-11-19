# FSOP — file stream oriented programming


FILE structures (_IO_FILE / _IO_jump_t) are function-pointer tables in
plain memory: corrupting vtable entries redirects stdio calls to
attacker code.

## Why it matters

- Works where hooks are gone (glibc >= 2.34).
- exit() and fflush drive the call — a reachable trigger.
- _IO_2_1_stderr_, _IO_2_1_stdout_, _IO_2_1_stdin_ have known libc
  addresses.

## The shape

1. Arbitrary write → overwrite a FILE's vtable pointer or a jump entry
   (e.g. _IO_file_jumps + offset).
2. Trigger the stdio call — exit(), fflush(NULL), a print error path.
3. The call dereferences your forged pointer → PC control.

## Version notes

- 2.24+: vtable check `_IO_vtable_check` — the vtable must point inside
  __libc_IO_vtables → forge into a known-valid vtable region minus a
  chosen offset, not arbitrary memory.

## Falsifier

No write reaches a FILE structure or its vtable, and no stdio call
fires after: FSOP unreachable.

# printf-family and the heap — stderr FILEs


stderr/stdout/stdin are FILE* globals in libc — the FSOP targets:
_IO_2_1_stderr_ is unbuffered and fires on abort/exit paths.

## The note

- _IO_2_1_stderr_ is reachable on error paths (a crash writes through
  it).
- The vtable must point inside __libc_IO_vtables (2.24+ check) — pick a
  nearby valid vtable and skew the call offset.
- _IO_wfile_jumps / _IO_file_jumps are the usual forgery anchors.

## Falsifier

The forged vtable fails the _IO_vtable_check: aim inside the tables
region instead.

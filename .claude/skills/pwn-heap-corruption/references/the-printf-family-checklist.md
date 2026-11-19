# printf-family and the heap — stderr FILEs — checklist

Companion to `the-printf-family.md`.

## Checklist

- [ ] _IO_2_1_stderr_ is reachable on error paths (a crash writes through
- [ ] The vtable must point inside __libc_IO_vtables (2.24+ check) — pick a
- [ ] _IO_wfile_jumps / _IO_file_jumps are the usual forgery anchors.

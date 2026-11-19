# Breakpoint strategy — where to pause — checklist

Companion to `r2-breakpoints.md`.

## Checklist

- [ ] Before the corrupting op (the overflow/UAF write): `db <addr>`.
- [ ] Inside _int_free after your free: watch the bin link happen.
- [ ] Inside _int_malloc on the harvest alloc: watch the return.
- [ ] On __libc_abort/glibc's error path: catch which check fired.

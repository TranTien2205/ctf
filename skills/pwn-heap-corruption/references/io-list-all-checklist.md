# _IO_list_all — the FILE chain head — checklist

Companion to `io-list-all.md`.

## Checklist

- [ ] 1. Write _IO_list_all = your fake FILE chain head.
- [ ] 2. Each fake FILE needs _chain → next fake; last → 0.
- [ ] 3. On exit()/abort, flush-all calls each FILE's vtable _IO_overflow —

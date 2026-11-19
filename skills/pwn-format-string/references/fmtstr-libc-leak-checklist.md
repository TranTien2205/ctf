# Leaking libc — the GOT-read path — checklist

Companion to `fmtstr-libc-leak.md`.

## Checklist

- [ ] 1. Non-PIE: the GOT slot address is fixed — plant it.
- [ ] 2. %N$s on the planted GOT-addr: prints the resolved libc function's
- [ ] 3. libc_base = leaked - symbol_offset (know the libc version).

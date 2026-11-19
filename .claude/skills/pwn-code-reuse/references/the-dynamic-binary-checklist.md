# The dynamic binary — the PLT/GOT surface — checklist

Companion to `the-dynamic-binary.md`.

## Checklist

- [ ] PLT entries: callable stubs for every import.
- [ ] GOT entries: resolved pointers — leak sources and (partial RELRO)
- [ ] The binary's own functions — win functions, gadgets.

# The dynamic binary — the PLT/GOT surface


A dynamically-linked binary imports functions via PLT/GOT — the call
surface is the PLT, the leak surface is the GOT, the libc is external.

## The surface

- PLT entries: callable stubs for every import.
- GOT entries: resolved pointers — leak sources and (partial RELRO)
  write targets.
- The binary's own functions — win functions, gadgets.

## Falsifier

None specific — the dynamic shape is the common case.

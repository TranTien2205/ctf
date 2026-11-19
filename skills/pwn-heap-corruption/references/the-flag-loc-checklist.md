# Where the flag lives — targeting the final read — checklist

Companion to `the-flag-loc.md`.

## Checklist

- [ ] system("/bin/sh") via hook/vtable → cat flag.
- [ ] Arbitrary read of a flag buffer → the flag bytes themselves.
- [ ] A write that sets the "authorized" flag → the gated path prints it.

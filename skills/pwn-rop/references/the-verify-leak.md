# Verifying the computed base — sanity


After computing libc_base:

- Is it page-aligned? (low 12 bits zero)
- Is it in the libc range? (0x7f....)
- Does base+offset of another symbol match a second leak?

## The cross-check

Leak two symbols; their distance must equal their offset delta.

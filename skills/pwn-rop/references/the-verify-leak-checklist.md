# Verifying the computed base — sanity — checklist

Companion to `the-verify-leak.md`.

## Checklist

- [ ] Is it page-aligned? (low 12 bits zero)
- [ ] Is it in the libc range? (0x7f....)
- [ ] Does base+offset of another symbol match a second leak?

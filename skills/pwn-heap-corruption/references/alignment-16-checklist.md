# The 0x10 alignment — size classes on x64 — checklist

Companion to `alignment-16.md`.

## Checklist

- [ ] request 0x0..0x18 → chunk 0x20.
- [ ] request 0x19..0x28 → chunk 0x30. etc.
- [ ] size field stores chunk size | flags — the low 3 bits are free.
- [ ] Bin placement is by chunk size — the real size, not the request.
- [ ] An off-by-NUL on size 0x101 → 0x100: still a valid aligned size.
- [ ] The low-3-bits are the flags — P=1, M=2, N=4.

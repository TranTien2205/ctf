# rdx substitutes — when pop rdx is missing — checklist

Companion to `the-rdx-substitutes.md`.

## Checklist

- [ ] `mov rdx, rXx; ret` where rXX you control.
- [ ] `xor edx, edx; ret` for NULL.
- [ ] ret2csu's mov rdx, r15 sequence.
- [ ] A `pop rXX`-that-aliases-rdx on some encodings.

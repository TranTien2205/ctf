# Args past rdi/rsi — the harder registers — checklist

Companion to `the-args-past-two.md`.

## Checklist

- [ ] rdx: `pop rdx` rare — `mov rdx, r15`-shaped or ret2csu.
- [ ] rcx/r8/r9: usually needed only for exotic calls — most chains stop

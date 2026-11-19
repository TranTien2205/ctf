# The two-class split — x86 vs x64 chains — checklist

Companion to `the-two-class.md`.

## Checklist

- [ ] x64: args in registers — pops set them; the chain is pop+arg pairs.
- [ ] x86: args on the stack — the chain is [func][ret][args...].

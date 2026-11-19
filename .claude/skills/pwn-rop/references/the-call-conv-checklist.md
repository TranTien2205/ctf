# The calling conventions — SysV vs Win vs x86 — checklist

Companion to `the-call-conv.md`.

## Checklist

- [ ] x64 SysV (Linux): rdi rsi rdx rcx r8 r9.
- [ ] x64 Windows: rcx rdx r8 r9 — different order!
- [ ] x86 cdecl: stack args.

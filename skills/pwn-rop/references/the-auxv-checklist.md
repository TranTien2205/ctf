# auxv — the kernel's hints — checklist

Companion to `the-auxv.md`.

## Checklist

- [ ] AT_BASE: ld.so's base.
- [ ] AT_ENTRY: the binary's entry — a PIE anchor.
- [ ] AT_SYSINFO_EHDR: the vDSO — syscall-free kernel calls.

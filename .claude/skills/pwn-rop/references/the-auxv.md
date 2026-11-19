# auxv — the kernel's hints


The auxiliary vector at the stack's top carries AT_PHDR, AT_BASE,
AT_ENTRY, AT_RANDOM, AT_SYSINFO_EHDR — addresses the kernel handed
the process.

## The leaks

- AT_BASE: ld.so's base.
- AT_ENTRY: the binary's entry — a PIE anchor.
- AT_SYSINFO_EHDR: the vDSO — syscall-free kernel calls.

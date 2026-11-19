# No imports — the static world


A static binary has no PLT/GOT — every call is a direct address; the
gadget surface is huge (the linked libc is in the binary).

## The consequence

- No GOT leak — instead, gadgets + syscall stubs.
- The syscall route is usually the path.
- "/bin/sh" may exist in the binary's rodata — or be planted.

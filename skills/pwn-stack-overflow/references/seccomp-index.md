# Seccomp — the syscall whitelist that shapes the payload — index

A seccomp filter restricts which syscalls the process may make: open may be banned while openat is allowed, execve banned entirely — the shellcode or syscall-chain must use only allowed calls.

## Related modules

- `seccomp-deep.md` — boundary conditions
- `seccomp-checklist.md` — operational steps
- `seccomp-catalogue.md` — case enumeration

## Cross-references

`ret2shellcode.md` · `tools-sc-gen.md`

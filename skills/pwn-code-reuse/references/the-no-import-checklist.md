# No imports — the static world — checklist

Companion to `the-no-import.md`.

## Checklist

- [ ] No GOT leak — instead, gadgets + syscall stubs.
- [ ] The syscall route is usually the path.
- [ ] "/bin/sh" may exist in the binary's rodata — or be planted.

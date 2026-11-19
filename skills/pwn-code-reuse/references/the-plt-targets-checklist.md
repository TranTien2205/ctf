# The PLT targets — what's callable — checklist

Companion to `the-plt-targets.md`.

## Checklist

- [ ] puts/printf/write — the leak channel.
- [ ] read/gets/scanf — the second-stage channel.
- [ ] system/execve — the ending (rarely present directly).
- [ ] malloc/free/mmap — heap/sys primitives.
- [ ] exit — the clean ending.

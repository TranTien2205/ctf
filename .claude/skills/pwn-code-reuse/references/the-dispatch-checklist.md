# The dispatch — choosing by the binary's shape — checklist

Companion to `the-dispatch.md`.

## Checklist

- [ ] Binary shape | The route
- [ ] static, has syscall | execve-by-syscall
- [ ] dynamic, imports system | ret2libc
- [ ] dynamic, no system | ret2dlresolve or gadget-built call
- [ ] has a win func | ret2win
- [ ] tiny, few gadgets | ret2csu or SROP

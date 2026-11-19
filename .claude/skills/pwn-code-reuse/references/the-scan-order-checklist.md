# The scan order — which gadget first — checklist

Companion to `the-scan-order.md`.

## Checklist

- [ ] 1. syscall (scarcest — decides static vs dynamic route)
- [ ] 2. pop rdx (scarce — needed for execve's envp)
- [ ] 3. pop rax (for the syscall number)
- [ ] 4. pop rsi
- [ ] 5. pop rdi (commonest)
- [ ] 6. ret, leave, mov-store

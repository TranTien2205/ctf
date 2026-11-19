# SROP — the sigreturn frame — checklist

Companion to `the-srop.md`.

## Checklist

- [ ] 1. pop rax ; 15 ; syscall — the rt_sigreturn call.
- [ ] 2. The next 248 bytes on the stack are the register frame — set them.
- [ ] 3. Execution resumes with all registers = your frame — rdi/rsi/rdx

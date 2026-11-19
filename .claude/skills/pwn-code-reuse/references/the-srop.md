# SROP — the sigreturn frame


sigreturn (syscall 15 on x64, 77 on x86, rt_sigreturn) loads ALL
registers from a frame on the stack — a full register-set in one call.

## The recipe (x64)

1. pop rax ; 15 ; syscall — the rt_sigreturn call.
2. The next 248 bytes on the stack are the register frame — set them.
3. Execution resumes with all registers = your frame — rdi/rsi/rdx
  AND rip — a full-context jump.

## When it helps

Gadgets too scarce for a normal chain — SROP sets everything at once.

## Falsifier

No syscall gadget or the frame can't fit: the normal chain is needed.

# The clobbered registers — what calls kill


Caller-saved (the callee may destroy): rax, rdi, rsi, rdx, rcx,
r8-r11 — a call kills them; callee-saved (rbx, rbp, r12-r15) survive.

## The chain rule

A value needed AFTER a call must live in a callee-saved register or
be re-set.

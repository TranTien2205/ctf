# Verifying the walk — the register trace


Under r2 -d, at each step: `dr rip rdi rsi rdx rax rsp` — the chain's
effect is measurable at every ret; the trace IS the verification.

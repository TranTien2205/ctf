# Frame fields — which matter


The fields the exploit cares about: rdi/rsi/rdx (the args), rax (the
next syscall number if chaining), rsp (the next stack), rip (the
next code) — the rest get sane defaults.

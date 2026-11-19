# Caller-saved registers — the casualties


rax, rcx, rdx, rsi, rdi, r8-r11 die at calls — re-set them after
each call, or don't rely on them post-call.

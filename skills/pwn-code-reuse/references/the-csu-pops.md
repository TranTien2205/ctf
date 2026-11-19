# The csu pops — the universal register setter


__libc_csu_init's tail gadget pops six registers:

    pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret

—and the middle gadget uses them:

    mov rdx, r15; mov rsi, r14; mov edi, r13d;
    call [r12+rbx*8]

The pair is the universal call when individual pops are missing.

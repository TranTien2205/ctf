# ret2csu — the universal call primitive


__libc_csu_init contains a gadget sequence that sets rbx/rbp/r12-r15
then CALLS *(r12+rbx*8) — a controllable call when individual pop
gadgets are missing.

## The gadgets (standard pattern)

    pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
    mov rdx, r15; mov rsi, r14; mov edi, r13d; call [r12+rbx*8]
    add rbx, 1; cmp rbx, rbp; jne ...; add rsp, 8; pop ...; ret

## The recipe

- Set r12 = &target_func_area, rbx = 0, rbp = 1 (or loop control),
  r13/r14/r15 = the args.
- The call fires through [r12+rbx*8] — a memory-indirect call.

## Falsifier

__libc_csu_init isn't present (very new/musl/static) or the needed
registers aren't settable by the pops: ret2csu is closed.

# Building ret2csu — the universal call


When pop gadgets are missing, __libc_csu_init's two fragments compose
a call with rdi/rsi/rdx set:

    gadget1 (tail):  pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
    gadget2 (mid):   mov rdx, r15; mov rsi, r14; mov edi, r13d;
                     call [r12+rbx*8]; add rbx,1; cmp rbp,rbx; jne ...;
                     pop rbx; ...; ret

## The setup

- rbx=0, rbp=1 (one iteration)
- r12 = &func_pointer_area (the call reads [r12])
- r13=rdi_arg, r14=rsi_arg, r15=rdx_arg
- After gadget2's call: 7 scratch qwords for its trailing pops.

## The find

    r2 -A ./chal ; pdf @ sym.__libc_csu_init | tail -30

# ret2csu — the universal gadget pair — checklist

__libc_csu_init carries two gadgets that set rdx, rsi, rdi, and call an arbitrary function — the fallback when the binary is sparse of clean pops.

## Checklist

- [ ] Check for __libc_csu_init: readelf -s ./chal | grep csu.
- [ ] The init gadget pops rbx,rbp,r12-r15; the body gadget uses them as rdx,rsi,edi and calls [r12+rbx*8].
- [ ] Set rbx=0 and r12 = GOT entry to call — the body does mov rdx,r15; mov rsi,r14; mov edi,r13d; call [r12+rbx*8].
- [ ] After the call it falls through to the init gadget's ret — continue the chain.

## Abort conditions

- r12 must hold the ADDRESS of a pointer to the function (a GOT slot), not the function itself.
- The body gadget's 'call' jumps to [r12+rbx*8] — an indirect call, not a ret-based transfer.
- r13d is edi (32-bit!) — zero the upper half if the arg needs 64 bits.

## Falsifier

Falsifier — statically linked or stripped binary without __libc_csu_init: the universal pair doesn't exist.

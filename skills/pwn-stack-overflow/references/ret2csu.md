# ret2csu — the universal gadget pair

__libc_csu_init carries two gadgets that set rdx, rsi, rdi, and call an arbitrary function — the fallback when the binary is sparse of clean pops.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| __libc_csu_init in symbols | universal gadgets exist | use the pair |
| no pop rdx gadget anywhere | csu supplies it | the pair |
| x64 dynamic binary | csu present | the pair |

## Steps

1. Check for __libc_csu_init: readelf -s ./chal | grep csu.
2. The init gadget pops rbx,rbp,r12-r15; the body gadget uses them as rdx,rsi,edi and calls [r12+rbx*8].
3. Set rbx=0 and r12 = GOT entry to call — the body does mov rdx,r15; mov rsi,r14; mov edi,r13d; call [r12+rbx*8].
4. After the call it falls through to the init gadget's ret — continue the chain.

## Falsifier

Falsifier — statically linked or stripped binary without __libc_csu_init: the universal pair doesn't exist.

## Traps

- r12 must hold the ADDRESS of a pointer to the function (a GOT slot), not the function itself.
- The body gadget's 'call' jumps to [r12+rbx*8] — an indirect call, not a ret-based transfer.
- r13d is edi (32-bit!) — zero the upper half if the arg needs 64 bits.

## Commands

```bash
readelf -s ./chal | grep csu
r2 -A ./chal && pdf @ __libc_csu_init
```

## Cross-references

`rop-basics.md` · `ret2libc.md`

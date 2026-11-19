# The ret2csu recipe — the full sequence — checklist

Companion to `the-csu-recipe.md`.

## Checklist

- [ ] 1. pop rbx=0, rbp=1 (loop ends after one call), r12=&func_area,
- [ ] 2. The call-gadget: [r12+0]=the function; args set from r13-r15.
- [ ] 3. The add/cmp/jne + the trailing pops to consume the extra frame.
- [ ] r12+rbx*8 is the call target — r12 points at a POINTER to the func.
- [ ] r13's low 32 bits go to edi — the first arg.

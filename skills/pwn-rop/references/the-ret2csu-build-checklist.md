# Building ret2csu — the universal call — checklist

Companion to `the-ret2csu-build.md`.

## Checklist

- [ ] rbx=0, rbp=1 (one iteration)
- [ ] r12 = &func_pointer_area (the call reads [r12])
- [ ] r13=rdi_arg, r14=rsi_arg, r15=rdx_arg
- [ ] After gadget2's call: 7 scratch qwords for its trailing pops.

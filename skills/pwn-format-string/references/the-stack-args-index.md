# The stack-args region — where high-N args live — index

x64 passes args 1-6 in registers (rdi,rsi,rdx,rcx,r8,r9); args 7+ are on the stack. The %N$p values at high N are stack memory — pointers, your input, the saved frame.

## Related modules

- `the-stack-args-deep.md` — boundary conditions
- `the-stack-args-checklist.md` — operational steps
- `the-stack-args-catalogue.md` — case enumeration

## Cross-references

`arg-offset-finder.md` · `width-precision-fields.md`

# x86 vs x64 argument layout — where your buffer sits — index

x86 puts all args on the stack (low N reaches your input); x64 puts the first 6 in registers (your input is at high N). The arg-offset differs fundamentally.

## Related modules

- `x86-vs-x64-args-deep.md` — boundary conditions
- `x86-vs-x64-args-checklist.md` — operational steps
- `x86-vs-x64-args-catalogue.md` — case enumeration

## Cross-references

`arg-offset-finder.md` · `the-stack-args.md`

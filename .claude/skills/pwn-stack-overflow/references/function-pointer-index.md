# Function-pointer overwrite — the indirect-call target — index

A function pointer stored on the stack (a callback, a handler table, an atexit entry) that's overwritten becomes a controlled call site — call instead of return.

## Related modules

- `function-pointer-deep.md` — boundary conditions
- `function-pointer-checklist.md` — operational steps
- `function-pointer-catalogue.md` — case enumeration

## Cross-references

`control-flow.md` · `write-where.md`

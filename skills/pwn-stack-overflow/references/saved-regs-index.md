# Saved registers — the frame layout — index

The stack frame: [locals][canary?][saved RBP][saved RIP][args]. Smashing past saved RBP hits saved RIP — the offset math lives here.

## Related modules

- `saved-regs-deep.md` — boundary conditions
- `saved-regs-checklist.md` — operational steps
- `saved-regs-catalogue.md` — case enumeration

## Cross-references

`offset-measurement.md` · `canary-bypass.md`

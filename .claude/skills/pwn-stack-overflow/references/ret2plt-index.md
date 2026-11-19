# ret2plt / ret2system — call an imported function — index

system@plt, puts@plt, printf@plt: imported functions have static PLT stubs even under PIE. If the binary imports system and you control a string argument, ret2plt is the shortest chain.

## Related modules

- `ret2plt-deep.md` — boundary conditions
- `ret2plt-checklist.md` — operational steps
- `ret2plt-catalogue.md` — case enumeration

## Cross-references

`ret2win.md` · `ret2libc.md` · `rop-basics.md`

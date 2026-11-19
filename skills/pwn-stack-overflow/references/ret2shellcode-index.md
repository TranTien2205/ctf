# ret2shellcode — when NX is off — index

NX off means the stack (or a buffer) is executable: write your shellcode, jump to it. tools/sc_gen.py emits tested stubs — no pwntools needed.

## Related modules

- `ret2shellcode-deep.md` — boundary conditions
- `ret2shellcode-checklist.md` — operational steps
- `ret2shellcode-catalogue.md` — case enumeration

## Cross-references

`tools-sc-gen.md` · `protection-modes.md` · `bad-chars.md`

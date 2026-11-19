# jmp rsp / call reg — the 'execute what's already there' transfer — index

Instead of writing shellcode past the saved RIP, a 'jmp esp'/'call esp' gadget jumps back INTO your own input on the stack — shellcode travels in the same bytes as the smash.

## Related modules

- `jmp-esp-deep.md` — boundary conditions
- `jmp-esp-checklist.md` — operational steps
- `jmp-esp-catalogue.md` — case enumeration

## Cross-references

`ret2shellcode.md` · `rop-basics.md`

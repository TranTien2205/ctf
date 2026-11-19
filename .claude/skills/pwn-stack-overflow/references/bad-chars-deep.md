# Bad characters — which bytes the input path strips — deep

The read function's allowed byte set determines which shellcode/chain bytes are legal. A banned byte kills the exploit silently.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — a needed address/opcode contains a banned byte and no equivalent exists: the chain must be reworked or the class is wrong.

## Highest-cost traps

- \x00 (null) always terminates C strings — in scanf %s it also ends input.
- \x0a (newline) ends fgets/line reads.
- A ROP chain with \x00 in an address needs the address rewritten via a mov gadget.

## Commands

```bash
python3 tools/sc_gen.py execve64 --raw   # reports any \x00\x0a\x0d\x20 bytes
```

## Cross-references

`ret2shellcode.md` · `read-family.md`

# ret2shellcode — when NX is off — deep

NX off means the stack (or a buffer) is executable: write your shellcode, jump to it. tools/sc_gen.py emits tested stubs — no pwntools needed.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — NX is on: no shellcode executes regardless of control; the chain must be code-reuse.

## Highest-cost traps

- Byte filters: reads stopping at \x00\x0a\x0d\x20 kill shellcode with those bytes — sc_gen reports which the stub contains.
- Stack addresses are ASLR'd — you need the buffer's real address, usually from a leak or a jmp rsp gadget.
- cat64 reads the flag file; rev64 gives a reverse shell (--host/--port).

## Commands

```bash
python3 tools/sc_gen.py execve64 --raw
python3 tools/sc_gen.py cat64 --path /flag --raw
python3 tools/sc_gen.py --selftest
```

## Cross-references

`tools-sc-gen.md` · `protection-modes.md` · `bad-chars.md`

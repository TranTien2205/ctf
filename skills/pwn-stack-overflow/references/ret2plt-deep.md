# ret2plt / ret2system — call an imported function — deep

system@plt, puts@plt, printf@plt: imported functions have static PLT stubs even under PIE. If the binary imports system and you control a string argument, ret2plt is the shortest chain.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — no exec-like import and no useful PLT target: ret2plt is out; ret2libc or code-reuse chains remain.

## Highest-cost traps

- system@plt needs /bin/sh reachable — find or write it.
- rdi is the first arg on x64 — pop rdi;ret is the gadget; tools/pwn_triage.py lists it.
- Some PLT stubs need a second ret for stack alignment before libc calls.

## Commands

```bash
readelf -s ./chal | grep FUNC
r2 -A ./chal && izz | grep -i sh
python3 tools/pwn_triage.py ./chal --gadgets
```

## Cross-references

`ret2win.md` · `ret2libc.md` · `rop-basics.md`

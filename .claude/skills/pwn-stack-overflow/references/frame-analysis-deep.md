# Frame analysis — reading the exact layout from disassembly — deep

The decisive pre-flight: disassemble the vulnerable function, map the locals/canary/saved-regs positions from the actual code — not the textbook model.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the disassembly shows a fully-bounded read: the model says no overflow; trust the code, not the hope.

## Highest-cost traps

- -fomit-frame-pointer removes the saved RBP — the layout shifts by 8.
- Compiler reorders locals — the buffer may sit AFTER other locals, closer to the canary.
- The cyclic-measured offset is the ground truth; the disasm explains it.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln>
r2 -A ./chal && afi @ <vuln>
```

## Cross-references

`saved-regs.md` · `offset-measurement.md`

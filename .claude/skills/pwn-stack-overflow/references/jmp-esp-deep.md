# jmp rsp / call reg — the 'execute what's already there' transfer — deep

Instead of writing shellcode past the saved RIP, a 'jmp esp'/'call esp' gadget jumps back INTO your own input on the stack — shellcode travels in the same bytes as the smash.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — NX is on: nothing on the stack executes; jmp esp is moot.

## Highest-cost traps

- x64: jmp rsp (not esp); the gadget name follows the register width.
- The shellcode follows the return address — no separate buffer needed.
- Bad bytes in the shellcode still matter — match the read's filter.

## Commands

```bash
r2 -A ./chal && /R jmp
python3 tools/pwn_triage.py ./chal --gadgets
```

## Cross-references

`ret2shellcode.md` · `rop-basics.md`

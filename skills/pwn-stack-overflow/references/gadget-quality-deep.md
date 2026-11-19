# Gadget quality — which gadgets are usable and which aren't — deep

Not all gadgets are equal: a 'pop rdi; ret' is clean; 'pop rdi; pop rbp; ret' consumes an extra slot; a conditional gadget needs the right flags.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the only available gadget for a needed register has a side-effect that breaks the chain: find a different chain shape.

## Highest-cost traps

- Each gadget's side-effects must be neutral or useful — a stray 'call' can crash.
- The essential set: pop rdi, pop rsi, pop rdx, syscall, ret.
- A missing pop rdx is the classic hole — ret2csu or mov rdx gadgets cover it.

## Commands

```bash
python3 tools/pwn_triage.py ./chal --gadgets
r2 -A ./chal && /R pop
```

## Cross-references

`rop-basics.md` · `ret2csu.md`

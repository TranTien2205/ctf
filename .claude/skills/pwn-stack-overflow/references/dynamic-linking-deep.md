# Dynamic linking internals — how PLT/GOT really work — deep

The PLT/GOT mechanism is the ret2plt/ret2libc/GOT-overwrite foundation: understand it and those chains write themselves.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — full RELRO binds everything at startup: no lazy path exists; GOT[x] is already the real addr.

## Highest-cost traps

- A 'puts(GOT[puts])' leak only shows the libc addr AFTER puts was called once — else it's the PLT addr.
- Full RELRO pre-resolves everything — GOT is readonly, no lazy path.
- The resolver is _dl_runtime_resolve — the ret2dlresolve target.

## Commands

```bash
readelf -r ./chal
objdump -d ./chal | grep -A3 plt
```

## Cross-references

`ret2plt.md` · `ret2libc.md` · `ret2dlresolve.md`

# Protection internals — what each mechanism actually does — deep

Each protection is a specific mechanism with a specific failure mode — knowing the internals tells you the bypass.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the protection doesn't behave as named (e.g., a static binary 'has' __stack_chk_fail but doesn't use it): read the evidence, not the import list.

## Highest-cost traps

- A static binary imports __stack_chk_fail even with -fno-stack-protector — the import lies.
- Partial RELRO leaves GOT writable; full RELRO makes it readonly at startup.
- ASLR is separate from PIE — a non-PIE binary has a static base even under ASLR.

## Commands

```bash
python3 tools/pwn_triage.py ./chal
readelf -h ./chal | grep Type
readelf -d ./chal | grep -iE 'relro|bind'
```

## Cross-references

`protection-modes.md` · `tools-pwn-triage.md`

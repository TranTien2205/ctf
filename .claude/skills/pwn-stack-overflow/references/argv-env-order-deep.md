# The argv/env layout — predicting stack contents — deep

argv and env sit at the top of the stack: the first bytes a main() frame sees. Their layout predicts what the uninitialized-read leaks and where your shellcode/string can live.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the environment layout differs from the assumed model (different argv, stripped env): the predicted address is wrong; re-derive it.

## Highest-cost traps

- Env-var strings are \x00-free but otherwise arbitrary bytes.
- The exact stack address depends on argv+env byte count — it shifts with the environment.

## Commands

```bash
./chal   # main's stack starts below argv/env
```

## Cross-references

`env-control.md` · `argv-control.md`

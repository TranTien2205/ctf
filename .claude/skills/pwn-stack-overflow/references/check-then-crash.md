# The crash that proves control — reading the fault correctly

A segfault is only evidence when the faulting register holds your bytes. Read the fault correctly: RIP for control, a data register for a write crash.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| RIP = pattern bytes | return control proven | the offset is right |
| fault address in write | a write crash, not return | the smash is writing |
| RIP = 0x41414141 | control proven | the smash reached RIP |
| RIP unchanged | didn't reach saved state | bound too short |

## Steps

1. Run under r2 -d or read the kernel's core/dmesg for the faulting register.
2. RIP = pattern bytes → the return was hijacked → measure offset.
3. Fault in the write path (mov to your controlled ptr) → a different primitive.
4. No RIP control → the write didn't reach saved state.

## Falsifier

Falsifier — RIP never holds controlled bytes at any tested length: no return-control exists at this bound.

## Traps

- The 'crash' is the signal; the register tells you WHICH crash.
- A SIGSEGV at a write into your input is a write-crash, not a return-crash.
- Remote: the service may not expose the register — infer from the disconnect behavior.

## Commands

```bash
r2 -d ./chal
python3 tools/pwn_cyclic.py --find <bytes>
```

## Cross-references

`offset-measurement.md` · `cyclic-offset.md`

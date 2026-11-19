# Stack alignment — the movaps crash

x64 libc functions (especially system, printf) use movaps on the stack, which faults on misaligned RSP. A chain that crashes on the call site needs an extra 'ret' gadget for alignment.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| system@plt crashes inside libc | alignment off by 8 | add a ret |
| works locally, crashes remotely | different stack parity | pad with ret |
| movaps in the faulting libc frame | alignment confirmed | the fix is a ret |

## Steps

1. If the libc call crashes with a segv at a movaps on the stack, RSP is misaligned.
2. Insert a 'ret' gadget (no-op) before the call to bump RSP by 8.
3. Test both parities — the needed alignment depends on where the chain entered.

## Falsifier

Falsifier — the crash isn't alignment (it's a real arg/register problem): the ret-pad doesn't fix it; re-debug the chain.

## Traps

- The classic symptom: 'works locally, crashes remotely' — a 16-byte alignment shift.
- An even vs odd number of returns before the call is what matters.

## Commands

```bash
r2 -A ./chal && /R ret
```

## Cross-references

`ret2libc.md` · `troubleshoot.md`

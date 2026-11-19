# Stack alignment — the movaps crash — case catalogue

x64 libc functions (especially system, printf) use movaps on the stack, which faults on misaligned RSP. A chain that crashes on the call site needs an extra 'ret' gadget for alignment.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | system@plt crashes inside libc | alignment off by 8 | add a ret |
| 2 | works locally, crashes remotely | different stack parity | pad with ret |
| 3 | movaps in the faulting libc frame | alignment confirmed | the fix is a ret |

## Falsifier

Falsifier — the crash isn't alignment (it's a real arg/register problem): the ret-pad doesn't fix it; re-debug the chain.

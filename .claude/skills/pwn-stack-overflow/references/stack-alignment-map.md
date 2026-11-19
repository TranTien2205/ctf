# Stack alignment — the movaps crash — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| system@plt crashes inside libc | alignment off by 8 | add a ret |
| works locally, crashes remotely | different stack parity | pad with ret |
| movaps in the faulting libc frame | alignment confirmed | the fix is a ret |

## Falsifier

Falsifier — the crash isn't alignment (it's a real arg/register problem): the ret-pad doesn't fix it; re-debug the chain.

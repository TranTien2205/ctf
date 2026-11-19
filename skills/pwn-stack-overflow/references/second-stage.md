# Two-stage exploits — leak first, then exploit

Many chains need two rounds: first a leak (canary, libc base, stack address), then the real payload built with the leaked values.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| need a leaked value in the payload | two-stage | leak then re-trigger |
| the service loops after the leak | re-triggerable | send stage 2 |
| one-shot only | can't re-trigger | single-shot chain or fork-brute |

## Steps

1. Stage 1: trigger the leak (format-string, uninitialized read, puts(GOT)).
2. Read the leaked value from the response.
3. Stage 2: trigger the overflow again, building the payload with the leaked value.
4. A forking or looping service re-triggers cleanly; a one-shot needs the chain in one go.

## Falsifier

Falsifier — the service doesn't re-trigger and the chain needs two stages: single-shot is required — combine the leak and the smash in one input if the protocol allows.

## Traps

- Fork-per-connection gives clean re-trigger; single-process doesn't.
- Same-connection re-trigger needs the service to loop back to the read.
- A canary/base leaked in stage 1 is valid only for that process.

## Cross-references

`canary-bypass.md` · `ret2libc.md`

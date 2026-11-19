# Two-stage exploits — leak first, then exploit — checklist

Many chains need two rounds: first a leak (canary, libc base, stack address), then the real payload built with the leaked values.

## Checklist

- [ ] Stage 1: trigger the leak (format-string, uninitialized read, puts(GOT)).
- [ ] Read the leaked value from the response.
- [ ] Stage 2: trigger the overflow again, building the payload with the leaked value.
- [ ] A forking or looping service re-triggers cleanly; a one-shot needs the chain in one go.

## Abort conditions

- Fork-per-connection gives clean re-trigger; single-process doesn't.
- Same-connection re-trigger needs the service to loop back to the read.
- A canary/base leaked in stage 1 is valid only for that process.

## Falsifier

Falsifier — the service doesn't re-trigger and the chain needs two stages: single-shot is required — combine the leak and the smash in one input if the protocol allows.

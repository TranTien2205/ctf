# Splitting the chain — staged payloads


A small overflow can't hold the full chain: split it across calls —
leak first, re-enter, then the real chain.

## The stages

- Stage 1: the leak chain + a ret back to main/the vuln function.
- Stage 2: the real payload with the now-known addresses.

## The requirement

The program must re-enter the vulnerable read — a loop, a second
prompt, a re-invocation.

## Falsifier

One-shot execution: everything must fit one overflow — pivot or
minimize.

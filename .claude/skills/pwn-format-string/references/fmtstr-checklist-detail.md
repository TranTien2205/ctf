# The end-to-end checklist — every gate


The ordered gates for a fmtstr exploit, each with its pass signal and
abort condition.

## Gates

1. printf(input) found — disassemble, confirm your input is the format arg.
2. %p reflects pointers — the primitive confirmed.
3. AAAA.%N$p → marker — the offset found.
4. write target chosen — GOT/ret/hook exists and reachable.
5. value composed — count arithmetic produces the bytes.
6. redirect fires — the output/flag lands.

## Falsifier

Any gate fails: stop, record, reassess the route. Each gate is cheap —
fail fast, never build past an unverified gate.

# The end-to-end checklist — every gate — checklist

Companion to `fmtstr-checklist-detail.md`.

## Checklist

- [ ] 1. printf(input) found — disassemble, confirm your input is the format arg.
- [ ] 2. %p reflects pointers — the primitive confirmed.
- [ ] 3. AAAA.%N$p → marker — the offset found.
- [ ] 4. write target chosen — GOT/ret/hook exists and reachable.
- [ ] 5. value composed — count arithmetic produces the bytes.
- [ ] 6. redirect fires — the output/flag lands.

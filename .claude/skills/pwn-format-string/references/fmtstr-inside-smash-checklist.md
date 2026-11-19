# Fmtstr inside a smash path — the composition — checklist

Companion to `fmtstr-inside-smash.md`.

## Checklist

- [ ] Observation | Meaning | Route
- [ ] printf(buf) then a read(buf,n) in the same path | fmtstr + smash | compose them
- [ ] the fmtstr leaks canary/base | the smash needs it | leak then smash
- [ ] the fmtstr writes a bound | the smash reaches further | the enabling write
- [ ] 1. Find the format call and the overflow read in the same flow.
- [ ] 2. Use the fmtstr to leak what the smash needs (canary, base).
- [ ] 3. Or use a %n write to change a bound the smash then exceeds.
- [ ] 4. Two primitives, one chain.

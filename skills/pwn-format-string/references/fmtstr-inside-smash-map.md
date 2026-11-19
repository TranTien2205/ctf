# Fmtstr inside a smash path — the composition — map

Companion to `fmtstr-inside-smash.md`.

## Shapes
| Observation | Meaning | Route |
|---|---|---|
| printf(buf) then a read(buf,n) in the same path | fmtstr + smash | compose them |
| the fmtstr leaks canary/base | the smash needs it | leak then smash |
| the fmtstr writes a bound | the smash reaches further | the enabling write |
## Steps
## Falsifier

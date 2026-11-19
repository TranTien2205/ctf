# stack-protector-strong vs -all — which functions get canaries — map

Companion to `stack-protector-strong.md`.

## Signals
| Observation | Meaning |
|---|---|
| the vuln function has no %fs:0x28 load | this function is unprotected |
| a different function has it | per-function protection |
| the binary 'has' __stack_chk_fail | imported, maybe unused here |
## Check
## Falsifier

# The loop service — multi-call exploitation — checklist

Companion to `fmtstr-loop-service.md`.

## Checklist

- [ ] 1. Call 1 — the leak: %p dump, name the addresses.
- [ ] 2. Call 2 — the write: plant pointer + %n composition.
- [ ] 3. Call 3 — read-back verify: %N$s on the slot confirms the value.
- [ ] 4. Each call is independent — N re-measured if the site changed.
- [ ] Leaked values usable in the NEXT call's payload.
- [ ] Failed writes retryable (idempotent slots).
- [ ] Stage separation — verify each before the next.

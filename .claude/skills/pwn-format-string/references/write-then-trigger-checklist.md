# Write-then-trigger — the timing of the redirect — checklist

Companion to `write-then-trigger.md`.

## Checklist

- [ ] GOT write → fires on the NEXT call of that import.
- [ ] Ret-addr write → fires at function return.
- [ ] Hook write → fires at the next malloc/free.
- [ ] A dead write (target never read again) never fires.
- [ ] 1. Write the redirect.
- [ ] 2. Trigger the firing event (cause the call/return/alloc).
- [ ] 3. The behavior change IS the confirmation.

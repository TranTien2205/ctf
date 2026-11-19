# Confirming the write — the read-back — checklist

Companion to `the-write-confirmation.md`.

## Checklist

- [ ] The target's value changed → the write landed.
- [ ] A second %s read shows it → the verification.
- [ ] A redirect that fires is also confirmation.
- [ ] 1. After the write, read the target back — %s or a re-trigger.
- [ ] 2. The changed bytes confirm the write landed.
- [ ] 3. A redirect that fires is also confirmation.

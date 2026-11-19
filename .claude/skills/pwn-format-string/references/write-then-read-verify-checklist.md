# Write-then-read verification loop — checklist

Companion to `write-then-read-verify.md`.

## Checklist

- [ ] 1. Call 1: %n write the target.
- [ ] 2. Call 2: %s or %p at the target's address — read it back.
- [ ] 3. Value matches → proceed; mismatch → re-derive N or the count.

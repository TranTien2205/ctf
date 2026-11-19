# Write-then-read verification loop


For two-shot services: write in call 1, read back the target in call 2 —
verify before relying on the redirect.

## Steps

1. Call 1: %n write the target.
2. Call 2: %s or %p at the target's address — read it back.
3. Value matches → proceed; mismatch → re-derive N or the count.

## Falsifier

The service is one-shot: no verification pass; make the write's effect
the confirmation.

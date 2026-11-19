# Pre-checking the redirect target's existence — checklist

Companion to `the-call-target-check.md`.

## Checklist

- [ ] 1. Binary targets: verify via nm/readelf/r2 that the address is real.
- [ ] 2. Libc targets: verify against the shipped libc.so's symbol table.
- [ ] 3. Never write a guessed address — the redirect crashes.

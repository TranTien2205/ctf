# Arbitrary-free — freeing where you choose — checklist

Companion to `the-arbitrary-free.md`.

## Checklist

- [ ] 1. Find the free-anywhere path (OOB delete, forged ptr field).
- [ ] 2. Prepare the target region: forge a fake chunk's size + next-size.
- [ ] 3. free(target) → bin; malloc → target returned.

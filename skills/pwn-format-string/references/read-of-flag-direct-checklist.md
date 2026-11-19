# Reading the flag directly — the %s one-shot — checklist

Companion to `read-of-flag-direct.md`.

## Checklist

- [ ] 1. strings -tx ./chal | grep flag → the flag's static address.
- [ ] 2. Plant it at a %N$s arg position; %s prints it.
- [ ] 3. Under PIE, leak the base first → flag_addr = base + offset.

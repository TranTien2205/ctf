# GOT under PIE — the slot address is base+offset — checklist

Companion to `fmtstr-pie-got.md`.

## Checklist

- [ ] 1. Leak a code pointer — compute the base.
- [ ] 2. GOT slot addr = base + the relocation offset.
- [ ] 3. readelf -r lists the GOT offsets.

# GOT under PIE — the slot address is base+offset


Under PIE, the GOT moves with the base: the write target's address =
pie_base + got_offset — leak the base first.

## Steps

1. Leak a code pointer — compute the base.
2. GOT slot addr = base + the relocation offset.
3. readelf -r lists the GOT offsets.

## Verify

    readelf -r ./chal

## Falsifier

No code ptr leaks: the GOT address stays unknown.

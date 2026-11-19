# Pre-checking the redirect target's existence


Every address you write must exist at runtime: the gadget must be in the
binary, the function imported, the libc symbol at that offset.

## Steps

1. Binary targets: verify via nm/readelf/r2 that the address is real.
2. Libc targets: verify against the shipped libc.so's symbol table.
3. Never write a guessed address — the redirect crashes.

## Commands

```bash
nm ./chal | grep -iE 'win|flag|main'
nm -D libc.so.6 | grep -iE ' system$'
```

## Falsifier

The target doesn't exist at the expected address: fix the offset/base
first.

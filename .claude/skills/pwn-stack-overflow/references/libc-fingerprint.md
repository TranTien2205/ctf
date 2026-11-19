# Libc fingerprinting — which libc is it?

A leaked libc address is only useful with the right libc VERSION's offsets: fingerprint the version from two leaked symbols or the libc.so the challenge ships.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a leaked libc addr but unknown version | offsets unknown | fingerprint |
| two leaked symbols | delta between them names the version | libc-database |
| challenge ships libc.so.6 | the exact version | use its symbols |

## Steps

1. If the challenge ships a libc.so.6 — use IT: nm/objdump on it for the real offsets.
2. No shipped libc: leak TWO different symbols' addresses; their offset-delta fingerprints the version.
3. Match against libc-database or a local libc list to pick the right offset table.
4. Once the version is known: system offset, /bin/sh offset, execve — all from that libc.

## Falsifier

Falsifier — the leaked address doesn't match any known libc version's deltas: the leak isn't a libc pointer, or the libc is nonstandard.

## Traps

- A single leaked address doesn't identify the version — you need two.
- The shipped libc.so.6 is authoritative — prefer it over fingerprints.
- Wrong-version offsets make the chain crash at the wrong address.

## Commands

```bash
nm -D libc.so.6 | grep -iE ' system$| execve$| puts$'
readelf -s libc.so.6 | grep system
```

## Cross-references

`ret2libc.md` · `pie-leak.md`

# Libc fingerprinting — which libc is it? — checklist

A leaked libc address is only useful with the right libc VERSION's offsets: fingerprint the version from two leaked symbols or the libc.so the challenge ships.

## Checklist

- [ ] If the challenge ships a libc.so.6 — use IT: nm/objdump on it for the real offsets.
- [ ] No shipped libc: leak TWO different symbols' addresses; their offset-delta fingerprints the version.
- [ ] Match against libc-database or a local libc list to pick the right offset table.
- [ ] Once the version is known: system offset, /bin/sh offset, execve — all from that libc.

## Abort conditions

- A single leaked address doesn't identify the version — you need two.
- The shipped libc.so.6 is authoritative — prefer it over fingerprints.
- Wrong-version offsets make the chain crash at the wrong address.

## Falsifier

Falsifier — the leaked address doesn't match any known libc version's deltas: the leak isn't a libc pointer, or the libc is nonstandard.

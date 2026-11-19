# Checklist — the crypto-rsa engagement

## Intake

- [ ] Parse every `n`,`e`,`c`; record the bit-lengths.
- [ ] Count `n`,`e`,`c` — the family is in the counts.
- [ ] Find the leak — `d`,`phi`,`dp`,`dq`,`qInv`,`p`-bits,`m`-partial.
- [ ] Read the keygen — `next_prime`,`getPrime(d)`,`seed`,`p-1`,`e=3`,no pad.
- [ ] A PEM → `n`,`e` only; a *partial priv* → the field that isn't redacted.

## Discriminate

- [ ] `crypto_attack.py list` — the inventory + bounds.
- [ ] Walk `attack-table.md` — first yes picks the id.
- [ ] Write down which row fired and *why*.

## Bound-check

- [ ] `wiener` `d<n^0.25` / `boneh-durfee` `d<n^0.292`.
- [ ] `coppersmith` window≥`n^0.25`.
- [ ] `small-e` `m^e<n` / `hastad` `≥e` n's.
- [ ] `common-modulus` `gcd(e1,e2)=1`.
- [ ] `fermat` `|p-q|` small / `pollard` `B`≥factor.
- [ ] A bound failed → record the negative → next row.

## Attack

- [ ] `crypto_attack.py <id> <flags>` — `<id> --help` for the args.
- [ ] Cheap before lattice — fermat, batch, small-e, common-mod, pollard, wiener.

## Verify

- [ ] `pow(m,e,n)==c` for `m`; `p*q==n` for `p`,`q`.
- [ ] `pow(c,d,n)==m` then `pow(m,e,n)==c` for a `d`.
- [ ] Strip the pad if `m` is a padded block.
- [ ] `eth-root` — try each `gcd` candidate.

## Record

- [ ] `solved/<name>/` + `classify_solve.py` + the evidence tuple.
- [ ] A dead end → `knowledge/attempts/` with each bound.
- [ ] `../field-notes.md` — the confirmed/proposed entry.

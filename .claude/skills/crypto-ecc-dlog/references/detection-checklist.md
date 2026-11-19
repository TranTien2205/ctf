# Detection checklist — run before naming the attack

## The inventory check

- [ ] Curve/group named: `p`, `a`, `b`, `G`, `n` written down (or curve name).
- [ ] Signatures inventoried: count, `r` list, `z` derivation chosen.
- [ ] Oracle/service shape noted.

## The family check

- [ ] `r` duplicates scanned.
- [ ] `smoothness --n <ord>` run for any dlog.
- [ ] Custom curve: `Δ == 0`? `#E == p`? checked.
- [ ] Nonce bound stated/inferable checked.
- [ ] Server point-validation checked (invalid curve).

## The route check

- [ ] Attack chosen by the discriminator, not guessed.
- [ ] `--sigs` format ready for ECDSA attacks.
- [ ] `--order` is `n`, not `p`.
- [ ] `required_signatures` met for lattice attacks.

## The verify plan

- [ ] `x·G == Q`/`g^x == h` check identified before solving.
- [ ] The flag path (forge/decrypt → `flag{…}`) understood.

## The budget check

- [ ] Cheapest compatible attack first (`reuse`/`smoothness`/`Δ` before lattice).

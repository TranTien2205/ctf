# Checklist — run before/after every solve

## Before solving

- [ ] Group named: curve/`p`/`n`/`G`/`g` written down.
- [ ] Signatures: `r` scanned for duplicates.
- [ ] `smoothness --n <order>` run for any dlog.
- [ ] Custom curve: `#E == p`? `Δ == 0`? checked.
- [ ] `z` convention picked (FIPS truncation first).
- [ ] `--order` is `n`, not `p`.
- [ ] `--sigs` file has `[r,s,z]` triples / `{"r","s","z"}`.

## During solve

- [ ] Cheapest compatible attack first (`reuse` before `hnp`, `smoothness`
      before `pohlig-hellman`).
- [ ] `hnp-ecdsa` sig count ≥ `required_signatures`.
- [ ] One falsifier per attack in view.

## After solve

- [ ] `x·G == Q` or `g^x == h` verified.
- [ ] `flag{`/`CTF{` present in the decoded output.
- [ ] `post-probe` recorded with the verbatim verify output.
- [ ] A fail → falsifier noted in `knowledge/attempts/`.
- [ ] A solve → `classify_solve.py` chain card.

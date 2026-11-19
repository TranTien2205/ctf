# Detection checklist — the read-run-list

## Artifact reads

- [ ] generator type named/fingerprinted.
- [ ] outputs extracted (raw, consecutive).
- [ ] shape/truncation noted.
- [ ] oracle endpoints noted.

## Gate reads

- [ ] count meets the attack floor.
- [ ] outputs normalized (ints, not hex/float/mod).
- [ ] `m`/`a`/`c`/taps/width/`low-bits` identified.
- [ ] seed window bounded (if seed-search).

## Route reads

- [ ] family picked (`lcg`/`lfsr`/`mt`/`xorshift`/`seed`).
- [ ] attack picked (`per-attack-*`).
- [ ] command composed (`payload-dictionary*`).

## Close reads

- [ ] verify planned (`predict == held-back`).
- [ ] flag shape expected.
- [ ] `post-probe` shape ready.

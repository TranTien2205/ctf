# Checklist deep — the run-list, every line annotated

## Before touching the target

- [ ] **`selfcheck.py` is green** — 30/30; a broken tree means broken tools.
- [ ] **the class is `crypto-prng`** — not `crypto-symmetric-oracle` /
  `misc-encoding` — the confusable classes are ruled out.
- [ ] **`crypto_attack.py list`** — the attack inventory is loaded;
  `lcg-recover`/`lcg-unknown-modulus`/`lcg-truncated`/`berlekamp-massey`/
  `lfsr-predict`/`lfsr-recover`/`mt19937-clone` are present.
- [ ] **`xorshift128.py --selftest`** passes — the xorshift CLI works.

## The inventory

- [ ] generator fingerprinted — `mt19937`/`xorshift`/`lfsr`/`lcg`/seed —
  or `os.urandom`/`secrets` → **stop, wrong class**.
- [ ] outputs collected — consecutive, raw ints, no gaps.
- [ ] output shape noted — int / hex / float / bit / `mod n` / `>>b`.
- [ ] oracle endpoints listed — where the stream comes from.
- [ ] seed/init visible — `seed=`/`srand`/timestamp/pid.

## The gate

- [ ] count meets the floor — 3/6/required/2w/624/4.
- [ ] outputs normalized — ints, not hex/float/mod/randint.
- [ ] params known — `m`/`a`,`c`/taps/width/`low-bits`/seed-window.
- [ ] alignment confirmed — consecutive, no reseed in the window.

## The route

- [ ] family picked — lcg/lfsr/mt/xorshift/seed.
- [ ] attack picked — the param-known column decides.
- [ ] command composed — real flags, `payload-dictionary*`.

## The solve

- [ ] attack run — `crypto_attack.py <id>` or `xorshift128.py`.
- [ ] a held-back output reserved for verification.

## The close

- [ ] `predict == held-back` — bit-for-bit, never skipped.
- [ ] the flag-object used — forged token / decrypted stream / won roll.
- [ ] `flag{`/`CTF{` read from the response/decrypted bytes.
- [ ] `post-probe` / `pre-flag` — evidence a substring of `--response`.
- [ ] `attempts`/`classify_solve`/`field-notes` written.
- [ ] falsifier recorded if killed — mechanism + reopen_if.

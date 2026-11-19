# Theory — the working facts

## The families

1. **Shift** — `c=p+k` — IC~0.066, one chi² min. Caesar/ROT/Atbash.
2. **Substitution** — `c=σ(p)` — IC~0.066, flat chi², ETAOIN-shaped freq.
3. **Polyalphabetic** — `c_i=p_i+k_{i mod L}` — IC~0.038, Kasiski `L`.
4. **Transposition** — `c=π(p)` — letters preserved, order scrambled.
5. **Encoding** — a structured alphabet, no key — `enc_detect.py`.

## The statistics

- **IC** — `Σn_i(n_i-1)/N(N-1)` — the collision probability. English ≈0.066;
  a bijection preserves it; a `L`-alphabet mix drops it toward 0.038.
- **chi²** — `Σ(o-e)²/e` per `k` — the shift's English-likeness; the min is `k`.
- **Kasiski** — `gcd` of repeated-n-gram gaps → `L`.
- **Tetragram** — `Σ log p(quad)` — the `subst` objective; the annealing swaps
  `σ` entries, keeps improvements, restarts on a plateau.

## The facts

- Caesar ⊂ substitution — a shift is a `σ`.
- `L` is the key *length* — Kasiski/IC estimate it; `L` Caesars find the key.
- `flag{`/`CTF{` at a position — the format leaks `σ`/`k`/`key`.
- A near-English `subst` — a partially-right `σ` — polish the flag positions.
- A layered cipher — `cipher_id` on each output.
- The charset is the first discriminator — `+/=`/hex/`01` → encoding.

## The verify

`pt` language + `enc(pt)=ct`.

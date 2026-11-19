# Common mistakes — the traps that cost time

## The count mistakes

- **Running `mt19937-clone` on 623 outputs** — 623 is one state word short,
  not one output short; the clone silently can't form.
- **`lcg-recover` on 2 outputs** — `a`,`c` are two unknowns; 2 outputs
  underdetermine. Need 3.
- **`berlekamp-massey` on <2·width bits** — the recurrence isn't pinned.

## The rawness mistakes

- **Feeding hex/float/`mod`-applied outputs** — the tool expects raw ints.
  Decode first.
- **Skipping a gap** — "consecutive" is the whole premise; a skipped index
  misaligns everything.
- **`random.random()` floats into `mt19937-clone`** — floats are
  `getrandbits(53)` pairs; recover the pair, not a 32-bit word.

## The flag mistakes

- **`--low-bits` = kept bits** — it's the DROPPED low bits.
- **`--taps` in 0-indexed convention** — the module uses 1-indexed-from-LSB.
- **`--modulus` = `p` when the state modulus is `n`** — wrong group.
- **`--outputs` as a Python list repr** — comma-separated ints, not `[1, 2]`.

## The reasoning mistakes

- **A statistical test as proof** — chi-square uniformity ≠ predictability.
  The only proof is `predict == held-back`.
- **Lattice before the dedupe** — for ECDSA-adjacent nonce shapes, a reused
  `k` is closed-form — check before reaching for `lcg-truncated`.
- **`os.urandom`/`secrets`** assumed crackable — it's CSPRNG, wrong class.

## The record mistakes

- **Recording "recovered" without `predict == held-back`** — the verify IS
  the evidence.
- **A paraphrased prediction** — `post-probe` checks evidence ⊆ response.

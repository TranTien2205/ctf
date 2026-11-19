# Vigenere variants — the `L`-coset family, annotated

## The family

`c_i = p_i + k_{i mod L} mod 26` — `L` Caesar shifts cycling. The `L`-coset
mix flattens the letters — IC ~0.038 — and Kasiski gives `L`.

## The variants

### Vigenere — `c = p + k`

The canonical — `vigenere --keylen L` → `L` Caesars.

### Beaufort — `c = k - p`

The *reciprocal* — `p = k - c` — a Vigenere-decode gives garbage; the
reciprocal gives `pt`.

### Variant-Beaufort — `c = p - k`

`p = c + k` — a Vigenere with negated key.

### Autokey — `key = primer + pt`

The running key is the plaintext itself — `p_i = c_i - p_{i-1}` after the
primer. No periodic `L` in Kasiski.

### Gronsfeld — digit-key Vigenere

`key` digits 0-9 — a 10-shift Vigenere.

### Running-key — a book/long key

`key` a long text — Kasiski fails; a crib / the key text needed.

### Keyed-alphabet Vigenere — over `σ`-alphabet

`L` shifts over a `KEYWORD`-mixed alphabet — `vigenere` gives the `L` cosets,
then `subst` per-coset.

## The detection — IC~0.038 + Kasiski `L`

- **IC ~0.038** — the `L`-mix flattens toward uniform.
- **Kasiski** — repeated n-gram gaps `gcd` → `L`.
- **IC-per-coset** — the `L` that makes coset-IC ~0.066.

## The solve

`vigenere --text [--keylen L|--key <word>]` — `L` cosets, `L` Caesars.

## The falsifier

No `L` produces language → `subst`/`π`/other; or a Beaufort/`autokey`.

## The verify

`p_i = c_i - k_{i mod L}` → language.

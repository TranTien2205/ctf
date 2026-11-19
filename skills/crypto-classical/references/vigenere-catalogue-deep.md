# Vigenere catalogue deep — the `L`-coset family, fully indexed

## The family — `c_i = p_i + k_{i mod L}`

`L` Caesar shifts cycling — the `L`-mix flattens the letters → IC ~0.038;
Kasiski gives `L`.

## The variants — the `L`-coset set

| Variant | The transform | The solve | The files |
|---|---|---|---|
| Vigenere | `c = p + k` | `vigenere --keylen L` | `vigenere-deep.md`,`vigenere-catalogue.md` |
| Beaufort | `c = k - p` | `p = k - c` (reciprocal) | `beaufort-autokey*.md` |
| Variant-Beaufort | `c = p - k` | `p = c + k` | `beaufort-autokey*.md` |
| Autokey | `key = primer + pt` | `p_i = c_i - p_{i-1}` | `beaufort-autokey*.md` |
| Gronsfeld | digit-key | `vigenere --key <digits>` | `polyalphabetic-variants.md` |
| Running-key | a book/long key | a crib / the key text | `polyalphabetic-variants.md` |
| Keyed-alphabet | `L` shifts over `σ`-alphabet | `vigenere` `L` → `subst` per-coset | `vigenere-*.md`,`multi-step-chains*.md` |

## The detection — IC~0.038 + Kasiski `L`

- **IC ~0.038** — the `L`-mix flattens toward uniform.
- **Kasiski** — repeated n-gram gaps `gcd` → `L`.
- **IC-per-coset** — the `L` that makes coset-IC ~0.066.

## The solve — `L` cosets, `L` Caesars

`vigenere --text [--keylen L|--key <word>]` — split `ct` into `L` cosets;
each coset's chi²-min is `k_j` — the key.

## The `L`-mis-estimate

`L'=k·L` gives a near-decode with periodic errors — try `L`/`L/2`/`2L`.

## The verify

`p_i = c_i - k_{i mod L}` → language.

## The falsifier

No `L` produces language → `subst`/`π`/other; or a Beaufort/autokey.

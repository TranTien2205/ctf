# Detection — the reads that name the family

## The first read

```bash
python3 tools/cipher_id.py --text 'CT'
# or piped: echo 'CT' | python3 tools/cipher_id.py
```

`cipher_id` reports the IC, the per-shift chi², the Kasiski `L`, the letter
frequency, and a family verdict. That output is the discriminator.

## The charset — cipher vs encoding

| Charset | Read |
|---|---|
| `+/=` (base64), `0-9a-f` (hex), `01` (binary), `.-`/`/` (morse) | `enc_detect.py` — an **encoding**, not a cipher |
| letters only, no spaces | a cipher — the statistics apply |
| letters+digits | a partial cipher — letters transformed, digits kept |
| `flag{`/`CTF{`/`SNT{`/`synt{` | the format leak — anchor positions |

## The IC — the collision probability

`IC = Σ n_i(n_i-1) / N(N-1)` — the probability two random letters match.

- **~0.066** — English-shaped → monoalphabetic (caesar/subst/atbash/affine) or
  a short text.
- **~0.038** — uniform-ish → polyalphabetic (vigenere) or random.
- **~0.05-0.066** — English letter counts, scrambled order → transposition.

## The chi² — the shift fit

`chi²(k) = Σ (o_i - e_{i+k})² / e_{i+k}` over the 26 letters — how well the
`ct` shifted by `k` matches English.

- **one deep minimum at `k`** → `caesar`.
- **flat, no min** → `subst` (a non-cyclic `σ`).

## Kasiski — the period

A repeated n-gram (≥3) at gap `g` → `g` is a multiple of `L` (the key length).
GCD the gaps → `L`.

- **a small `L`** → `vigenere --keylen L`.
- **no repeated n-gram** → a short `ct` or `L` large.

## The frequency — the shape

- **ETAOIN-shaped** → monoalphabetic (the shape survives `σ`).
- **Reversed-ETAOIN** (Z,V,G common) → `atbash`.
- **Flat** → polyalphabetic or random.
- **English counts, scrambled order** → transposition.

## The verdict → the route

`cipher-identification.md` maps the (IC, chi², Kasiski, charset) tuple to the
family. The verdict is a *lead*, not a route — the solve verifies it.

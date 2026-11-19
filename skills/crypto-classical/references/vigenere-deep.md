# vigenere deep — the polyalphabetic, annotated

## The transform

`c_i = p_i + k_{i mod L} mod 26` — `L` Caesar shifts cycling. The key is a word
of length `L`; each letter's shift applies to one coset.

## The variants

- **Vigenere** — `c = p + k`.
- **Beaufort** — `c = k - p` — the reciprocal (decrypt = encrypt).
- **Variant Beaufort** — `c = p - k`.
- **Autokey** — the key is `primer + plaintext` — the plaintext supplies the
  running key.
- **Gronsfeld** — a Vigenere with key digits 0-9.
- **Keyed-alphabet Vigenere** — over a `σ`-mixed alphabet → `subst` after.

## The detection — the signal

`cipher_id` on a Vigenere `ct`:
- **IC ~0.038** — the `L`-alphabet mix flattens toward uniform.
- **Kasiski** — a repeated n-gram at gap `g` → `g` a multiple of `L`. GCD the
  gaps → `L`.
- **IC-per-coset** — the `L` that makes each coset's IC rise to ~0.066 is the
  period.

## The solve

```bash
python3 tools/classical_solve.py vigenere --text 'CT'               # IC/Kasiski → L → key
python3 tools/classical_solve.py vigenere --text 'CT' --keylen 5    # force L=5
python3 tools/classical_solve.py vigenere --text 'CT' --key LEMON   # a known key
```

```python
# manual — L cosets, chi² each
L = 5
key = ''.join(chr(65 + min(range(26),
                key=lambda k: chi2(coset_shift(ct[j::L], k))))
              for j in range(L))
```

## The polish

- **A near-decode with a wrong `L`** — `L` mis-estimated → re-estimate the
  period (try `L`, `L/2`, `2L`).
- **The key is a word** — the challenge text's obvious words first
  (`LEMON`,`SECRET`, the title, `key`), before Kasiski.
- **Autokey** — the plaintext-as-key decode: `k = primer + pt`.
- **Short `ct`** — under ~30 chars the statistics fail; the format positions
  carry the solve.

## The verify

`key` → `p_i = c_i - k_{i mod L}` → language; re-encrypt reproduces `ct`.

## The falsifier

No `L` produces language → not Vigenere → `subst`/transposition/other.

## The trap

- `L=1` → Vigenere = Caesar.
- A Beaufort `ct` Vigenere-decrypted gives the *reverse* key — try `c=k-p` too.

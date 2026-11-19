# vigenere catalogue — the polyalphabetic, every variant

## The family

`c_i = p_i + k_{i mod L} mod 26` — `L` shift alphabets cycling.

## The variants

- **Vigenere** — `c = p + k`.
- **Beaufort** — `c = k - p` — the reverse.
- **Variant Beaufort** — `c = p - k`.
- **Autokey** — the key is the plaintext appended after a primer.
- **Gronsfeld** — a numeric key `0-9`.
- **Keyed Caesar-alphabet** — Vigenere over a keyed alphabet → `subst` after.

## The detection

- IC ~0.038 — flattened.
- Kasiski — the `L`.
- A "key"/"vigenere"/"polyalphabetic" name.

## The solve

```bash
classical_solve vigenere --text 'CT'               # IC/Kasiski -> L -> key
classical_solve vigenere --text 'CT' --keylen L    # force the period
classical_solve vigenere --text 'CT' --key LEMON   # a known key
```

```python
# manual — L cosets, chi-squared each
L = 6
key = ''.join(min(range(26), key=lambda k: cs(coset_shift(ct[j::L],k)))
              for j in range(L))
```

## The polish

- A near-decode with a wrong `L` → re-estimate.
- The key a word → try the challenge-text words first.
- An autokey → the plaintext-as-key decode.

## The verify

`key` → `p = c - k_{i mod L}` → language; re-encrypt reproduces `ct`.

## The falsifier

No `L` produces language → not Vigenere → `subst`/transposition/other.

# caesar deep — the shift cipher, annotated

## The transform

`c_i = p_i + k mod 26` — a single shift `k` applied to every letter. `k` is the
whole key: 26 possible values, 25 useful (`k=0` is identity).

## The variants

- **Caesar** — `k` arbitrary.
- **ROT13** — `k=13`, self-inverse (`ct(ct(p))=p`).
- **ROT5** — digits only, `d_i = (d_i + 5) mod 10`.
- **ROT18** — letters ROT13 + digits ROT5.
- **ROT47** — printable ASCII 33-126 rotated by 47.
- **Atbash** — `c = 25 - p`, a *reflection* not a rotation — see `atbash-deep.md`.
- **Keyed Caesar** — a shift applied over a keyed alphabet → `subst`.

## The detection — the signal

`cipher_id` on a Caesar `ct`:
- **IC ~0.066** — a shift preserves English collision probability; `σ` is a
  rotation of the letter order, so the *shape* of the multiset is preserved
  cyclically.
- **chi² has exactly one deep minimum** at `k` — the shift that aligns the `ct`
  frequencies back to English. `E` (0.127 in English) shifted by `k` lands at
  `E+k`; the chi² minimum is the `k` that puts the biggest `ct` spike back on
  `E`,`T`,`A`,...

## The solve

```bash
python3 tools/classical_solve.py caesar --text 'WKHHDWHUHDWGVZQ'
# → the 25 shifts ranked by chi²; the min is k=3 → 'THEEATERATSW...'
```

```python
# manual — try all 25
for k in range(26):
    print(k, ''.join(chr((ord(c) - 65 - k) % 26 + 65) for c in ct))
# rot13 — self-inverse
import codecs; codecs.decode(ct, 'rot13')
```

## The polish — when the decode is *almost* right

- **Letters shifted, digits kept** — a partial shift (digits exempt).
- **A keyed alphabet** — the `k`-shifted letters look *almost* English →
  `subst` on the output (a shift composed with a keyed alphabet is a `σ`).
- **ROT5/18/47** — `codecs` or a script.

## The verify

`k` produces language; re-shifting `pt` by `k` reproduces `ct`. `flag{`/`CTF{`
present.

## The falsifier

No `k` produces language → not a shift → `subst` (a non-cyclic `σ`) or
transposition.

## The trap

`ROT13` on a *plaintext* reads as `ct` — `flag{` under ROT13 becomes
`synt{` — decode it back. A `flag{` that reads as `synt{`/`Pxl`/`fhpnf` is a
partially-encoded flag — decode the encoding, not the format.

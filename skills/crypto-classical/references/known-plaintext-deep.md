# Known-plaintext deep — the crib, annotated

## The crib

A known `pt` fragment — `flag{`, `CTF{`, `HTB{`, a greeting, a format — gives
`σ`/`k`/`key` directly. The format is the strongest crib: `flag{` at a known
position pins the transform's parameters at those positions.

## The Caesar crib

`flag{` at position `i` → `ct[i]` is `f`+k → `k = ct[i] - 'f'` (mod 26). One
position determines `k` — decode the whole `ct`. `flag{` → `IODJ{` → `k=?`.

## The Vigenere crib

`flag{` at position `i` → `k_{i mod L} = ct[i] - 'f'` — the crib fills `L`
key letters. `len(crib) ≥ L` → the whole key recovered; `len(crib) < L` → the
partial key constrains the anneal.

## The subst crib

`flag{` at positions → `σ⁻¹(ct[j]) = 'flag{'[j]` — the crib anchors `σ` at
those positions. A 5-letter crib anchors 5 `σ` entries — `σ⁻¹(ct[0])='f'`,
`σ⁻¹(ct[1])='l'`, `σ⁻¹(ct[2])='a'`, `σ⁻¹(ct[3])='g'`, `σ⁻¹(ct[4])='{'`. The
anneal finishes the rest.

## The transposition crib

`flag{` *letters* in the `ct` (in some order) → a `π` — the crib anchors the
*positions*: `f` must map to `ct[pos]` where `pos = π⁻¹(i)` — the `π` shape
revealed.

## The layered crib

The `flag{` is the *innermost* layer — the outer layers' cribs are their own
formats (a base64 `ct`'s `+/=` charset, a Morse's `.-`).

## The ROT13/partial-shift crib

`SNT{`/`synt{`/`Pxl{`/`fhpnf{` — the flag format *itself* under a `k`-shift —
decode the format to find `k`, then the `ct`.

## The verify

`enc(pt) == ct` — the crib + the decode confirm.

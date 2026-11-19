# Known-plaintext — when a crib anchors the solve

## The crib

A known `pt` fragment — `flag{`, `CTF{`, a greeting, a format — gives the
`σ`/`k`/`key` directly.

## The Caesar crib

`flag{` at position 0 → `ct[0]` is `f`+k → `k = ct[0] - 'f'`. One position
determines `k` — decode the whole `ct`.

## The Vigenere crib

`flag{` at position `i` → `k_{i mod L} = ct[i] - 'f'` — the crib fills `L`
key letters. If `L ≤ len(crib)` the whole key is recovered.

## The subst crib

`flag{` at positions → `σ⁻¹(ct[j]) = 'flag{'[j]` — the crib anchors `σ` at
those positions. A 5-letter crib anchors 5 `σ` entries — the anneal finishes.

## The transposition crib

`flag{` *letters* in the `ct` (in some order) → a `π` — the crib anchors the
*positions*: `f` must map to `ct[pos]` where `pos = π⁻¹(0)` — the `π` shape
revealed.

## The layered crib

The `flag{` is the *innermost* layer — the outer layers' cribs are their own
formats (a base64 `ct`'s `+/=` charset, a Morse's `.-`).

## The verify

`enc(pt) == ct` — the crib + the decode confirm.

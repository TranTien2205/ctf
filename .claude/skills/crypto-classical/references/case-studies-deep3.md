# Case studies deep 3 — the layered and crib shapes

## The `π(σ(p))` layered — order matters

A `ct` with English counts but scrambled order *and* non-English letters — a
transposition of a substituted text. `cipher_id` reads IC~0.05-0.066 (the `π`
preserves the multiset) but the freq isn't English — `π(σ(p))`.

**The solve**: un-scramble `π` *first* (rail-fence/columnar by `n` — the
position-permutation is independent of `σ`), then `subst` the un-scrambled
`ct` → `flag{...}`.

## The `enc → cipher → enc` layered

`ct` → `cipher_id` → "encoding" → `enc_detect` → a `caesar` `ct` →
`cipher_id` → "caesar" → `caesar` → a `morse` `ct` → `enc_detect` →
`flag{...}` — three independent decodes, `cipher_id` on each output.

## The keyed-alphabet Vigenere

`cipher_id` → `vigenere` (IC~0.038, Kasiski `L`) → `vigenere --keylen L` →
the `L` cosets decode to a `σ`-monoalphabetic (the `k` was over a `KEYWORD`
alphabet) → `subst` the output → `flag{...}`.

## The crib-anchored solve — `flag{` at pos 0

`ct` starts `gsdh{` — `flag{` at pos 0-4 → `σ⁻¹(g)=f`,`σ⁻¹(s)=l`,`σ⁻¹(d)=a`,
`σ⁻¹(h)=g` → the `σ` anchored → `subst` polishes the rest → `flag{...}`.

## The ROT13 flag — `synt{`

`ct` reads `synt{...}` — `flag{` under `k=13` — `codecs.decode(ct,'rot13')` →
`flag{...}` — the flag *is* the encoded form.

## The verify

`pt` language + `enc(pt)=ct` — each layer and the final.

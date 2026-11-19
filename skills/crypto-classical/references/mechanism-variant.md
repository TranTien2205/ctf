# Mechanism variant — the transforms, by family

## The shift — `c = p + k mod 26`

`caesar`/`ROT`/`atbash` — a cyclic rotation (`k`) or a reflection (`25-p`).
IC ~0.066; chi² finds `k` (one min) or the reversed ETAOIN.

## The substitution — `c = σ(p)`

`subst`/affine/keyword — a bijection. IC ~0.066, chi² flat, ETAOIN-shaped —
the multiset is renamed. The anneal climbs tetragrams.

## The polyalphabetic — `c_i = p_i + k_{i mod L}`

`vigenere`/beaufort/autokey/gronsfeld — `L` cycling shifts. IC ~0.038 (the
`L`-mix flattens); Kasiski gives `L`. `L` Caesars recover the key.

## The transposition — `c = π(p)`

`railfence`/columnar/route/scytale/block-perm — a position-permutation. IC
~0.05-0.066 — English counts, scrambled order; the multiset is *identical*.

## The encoding — `c = enc(p)`, no key

base64/hex/binary/morse/baconian/polybius/adfgvx — a fixed positional code —
`enc_detect` decodes; the charset is the tell.

## The compositions — `π(σ(p))` / `σ(π(p))` / keyed-alphabet Vigenere

- `π(σ(p))` — `π` first (position-only), then `subst`.
- `σ(π(p))` — `σ` first, then `π`.
- keyed-alphabet Vigenere — `vigenere` `L` cosets, then `subst` per-coset.

## The verify

`pt` language + `enc(pt)=ct`.

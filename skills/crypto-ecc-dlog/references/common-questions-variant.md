# Common questions variant — the FAQ, restated by situation

## "Two signatures — enough?"

Same `r` → `ecdsa-nonce-reuse`, done. Different `r` → only with a `k`
bound → `hnp-ecdsa`. One signature → nothing works on it alone.

## "`--order` is which number?"

`n` — the subgroup order `ord(G)` (curves) or `ord(g)` (fields), never `p`.

## "`--sigs` format?"

JSON **file** — `[{"r","s","z"}]` or `[[r,s,z]]`; `z` = hash-as-int.

## "What's `z`?"

`int(H(m))` truncated to `order_bits` (FIPS); `mod n` is the fallback
convention.

## "Lattice slow — why?"

Pure-python `lll.py`, `m+1` dims — keep `m` near `required_signatures`.

## "`d` plausible but doesn't verify?"

Wrong — `z`, `order`, bound, or attack. A scalar not reproducing the
public key is not the key.

## "Curve params but no `n`?"

Count `#E` (small `p`) → `smart_attack` if `== p`; `Δ == 0` → `singular_ec`;
else the intent is defect, not generic dlog.

## "`h = g^x mod p` but `p` huge?"

`smoothness --n p-1` — largest factor ≤ 2⁴⁰ → `pohlig-hellman`; bounded
`x` → `bsgs`; safe-prime → look elsewhere.

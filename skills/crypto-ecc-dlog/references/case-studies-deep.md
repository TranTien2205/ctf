# Case studies deep — the solve narrated

## Case 1 — `ecdsa-nonce-reuse` end to end

Handout: `sigs.txt` with two `(r, s, z)` rows, `r` identical, `n` = P-256
order, `Q` given.

```
sigs.json ← [{"r":r,"s":s1,"z":z1},{"r":r,"s":s2,"z":z2}]
crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order 0xFF..FF
→ d = 0x…
ec.py verify: E.mul(G, d) == Q ✓
flag{d_n0nc3_r3us3d}
```

Time: one command after the `r` scan.

## Case 2 — `hnp-ecdsa` on a signing service

Service signs arbitrary `m` on secp256k1, "nonce is 128 bits". Collect
~4–6 sigs (`required_signatures(256, 128)` ≈ 4):

```
crypto_attack.py hnp-ecdsa --sigs sigs.json \
  --order 0xFFFF..4141 --nonce-bits 128 --curve secp256k1 --pubkey 04..
→ d
verify d·G == Q ✓
```

## Case 3 — `pohlig-hellman` on a smooth subgroup

`h = g^x mod p`, `p` ~200-bit, `p-1 = 2·q₁·q₂·q₃` with `q_i` ≤ 2⁴⁰:

```
smoothness --n (p-1) → factors ✓
pohlig-hellman --g g --h h --p p --order (p-1) → x
pow(g, x, p) == h ✓
```

## Case 4 — `smart_attack` on an anomalous curve

Custom `p, a, b`; `#E` counted = `p`:

```
tools/crypto/smart_attack.py solves Q = x·P → x
x·P == Q ✓
```

## Case 5 — invalid-curve on a DH oracle

Service computes `d·P'` without validation:

```
for each fake curve E'_i with smooth ord(P'_i):
    submit P'_i → get d·P'_i → bsgs → d mod ord(P'_i)
CRT → d → d·G == Q ✓
```

## The shared close

Every case ends at `x·G == Q`/`g^x == h` — the verify is what makes it a
solve, not a candidate.

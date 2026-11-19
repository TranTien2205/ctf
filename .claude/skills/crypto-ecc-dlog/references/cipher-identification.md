# Identification — the handout → the attack table

## The input shapes → the route

| Handout | Attack | Command |
|---|---|---|
| two `(r, s)` with same `r` | `ecdsa-nonce-reuse` | `crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order n` |
| many `(r, s, z)`, distinct `r`, bounded `k` | `hnp-ecdsa` | `crypto_attack.py hnp-ecdsa --sigs sigs.json --order n --nonce-bits B` |
| leaked `k` bits per signature | `hnp`/`hnp-ecdsa` | `crypto_attack.py hnp --t t.json --u u.json --modulus n --bound B` |
| `h = g^x mod p`, `p-1` smooth | `pohlig-hellman` | `crypto_attack.py pohlig-hellman --g g --h h --p p --order n` |
| `h = g^x mod p`, `x` bounded | `bsgs` | `crypto_attack.py bsgs --g g --h h --p p --order n` |
| order `n` unknown/smoothness check | `smoothness` | `crypto_attack.py smoothness --n n` |
| `#E == p` | Smart's attack | `tools/crypto/smart_attack.py` |
| `4a³+27b² ≡ 0` | singular cubic | `tools/crypto/singular_ec.py` |
| server skips on-curve check | invalid curve | manual — `tools/crypto/ec.py` |

## The decision order

1. Are there signatures? → nonce family (`reuse` before `hnp`).
2. Is it `y = g^x` or `Q = x·G`? → dlog family (`smoothness` first).
3. Custom curve params? → defect family (`n == p`, singular, invalid).
4. None of the above? → probably not this class — re-route.

## The `--sigs` file format

```json
[
  {"r": "0x...", "s": "0x...", "z": "0x..."},
  {"r": 123, "s": 456, "z": 789}
]
```

List of `[r, s, z]` triples or `{"r","s","z"}` objects; hex strings and ints
both accepted. `z` = hash of the signed message as integer.

## The order problem

`--order` is the group order `n` — on named curves it's published; on custom
curves the challenge usually supplies it. If absent: count points with
Schoof-like methods (out of scope) — usually the challenge intends a
defect-curve attack instead.

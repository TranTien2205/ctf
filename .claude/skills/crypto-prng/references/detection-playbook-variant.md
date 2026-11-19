# Detection playbook variant — the branch tree, compact

```
outputs
 ├─ bits        → LFSR family
 │   └─ taps?   → lfsr-predict | BM → lfsr-recover → predict
 ├─ ints mod m  → LCG
 │   ├─ m known → lcg-recover
 │   ├─ m?      → lcg-unknown-modulus
 │   └─ x>>b    → lcg-truncated --low-bits
 ├─ 624 words   → MT → mt19937-clone
 ├─ 4 words     → xorshift128
 ├─ floats      → random()/Math.random → normalize/variant
 ├─ time-coupled→ seed-search
 └─ none/urandom→ OUT
```

## The gate before each

| Family | Gate |
|---|---|
| LCG | 3/6/required outs, raw ints |
| LFSR | 2w bits |
| MT | 624 raw words |
| xorshift | 4 words |
| seed | bounded window |

## The verify after each

`predict == held-back` — the one accept.

## The out signals

`os.urandom`/`secrets`/`crypto.`/`SecureRandom`/`arc4random`/`AES`/`HMAC`
→ reclassify.

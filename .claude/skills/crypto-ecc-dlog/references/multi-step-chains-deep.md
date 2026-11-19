# Multi-step chains deep — the composed attacks in full

## Chain A — `oracle → reuse → forge`

```
POST /sign {m1} → (r, s1)      POST /sign {m2} → (r, s2)   (same r)
crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order n → d
sign({"role":"admin"}) with d → token → GET /flag → flag{...}
```

The signature verify `d·G == Q` is the checkpoint before forging.

## Chain B — `oracle → biased k → d → sign`

```
collect N sigs (distinct r) →
crypto_attack.py hnp-ecdsa --sigs f --order n --nonce-bits B → d →
forge admin message → flag
```

`required_signatures` tells you N up front — don't over-collect.

## Chain C — `dlog → DH shared secret → AES decrypt`

```
handout: p, g, g^a mod p, g^b mod p, ct
smoothness → pohlig-hellman → a (or bsgs)
shared = (g^b)^a mod p → AES key → decrypt ct → flag
```

## Chain D — `defect curve → x → decrypt`

```
params → Δ/#E checks → smart_attack or singular_ec → x
x is the key → decrypt → flag
```

## Chain E — `point oracle → CRT → d`

```
for each E'_i (smooth ord):
    submit P'_i → d·P'_i → bsgs → d mod ord(P'_i)
CRT over Π ord(P'_i) ≥ n → d → verify → flag
```

## Chain F — `leaked bits → hnp → d`

```
oracle returns k masked/partial per sig
→ (t,u) transform → hnp --t f --u f --bound B → d → flag
```

## The chain-close rule

Every chain ends at `x·G == Q`/`g^x == h` then the application step
(decrypt/forge). A scalar without the flag step is a candidate, not a solve.

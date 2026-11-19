# Multi-step chains variant — the composed attacks restated

## The `reuse → forge` chain

```
sign(m1) → (r, s1)
sign(m2) → (r, s2)      same r
ecdsa-nonce-reuse → d
sign({"role":"admin"}) → GET /flag → flag
```

## The `bias → d → sign` chain

```
sign(m_i) ×N → sigs.json → hnp-ecdsa --nonce-bits B → d → forge → flag
```

## The `dlog → DH → decrypt` chain

```
p, g, g^a, g^b, ct → smoothness → pohlig-hellman → a
→ shared = (g^b)^a → AES key → decrypt ct → flag
```

## The `defect → x → decrypt` chain

```
params → Δ/#E → smart/singular → x → decrypt → flag
```

## The `oracle → CRT` chain

```
for E'_i smooth: multiply(P'_i) → d·P'_i → bsgs → d mod ord_i
CRT → d → verify → flag
```

## The `leak → hnp → d` chain

```
sign responses carry k_i partial → (t,u) → hnp → d → flag
```

## The boundary

Crypto step → flag step — the scalar is `class` evidence; the flag in
decoded bytes is `impact`. Both belong to the chain.

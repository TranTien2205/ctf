# Multi-step chains — crypto-classical meets the service

## `sign → verify → flag`

```
oracle.sign(m) → (r, s, z)         collect N sigs
ecdsa-nonce-reuse or hnp-ecdsa → d
sign the admin message → token → flag
```

## `dlog → session key → decrypt`

```
handout: p, g, h, params
smoothness → pohlig-hellman or bsgs → x
x is a DH shared secret → AES decrypt → flag
```

## `defect curve → scalar → flag`

```
params p, a, b → #E == p → smart_attack → x
or Δ == 0 → singular_ec → x
x decrypts the flag / signs
```

## `nonce leak → key → forge`

```
oracle returns partial k per signature
transform to (t, u) → hnp → d
d signs a forged JWT/message → flag
```

## `point oracle → CRT`

```
service computes d·P' on submitted point (no validation)
choose P'_i on smooth-order fake curves via ec.py
bsgs/pohlig per response → d mod m_i → CRT → d
```

## The layered boundary

When the crypto step feeds a web step (token forging, flag retrieval through
an endpoint), the crypto side is this class; the web side routes to
`web-*` skills after the scalar lands.

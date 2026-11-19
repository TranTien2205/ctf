# Scenarios deep — the challenge archetypes, expanded

## "The signer" — a sign endpoint

```
POST /sign {"msg": "..."}  →  {"r": ..., "s": ...}
```

Probe twice on same `m` — same `(r,s)` → deterministic `k`; different →
random `k`. If deterministic and `r` differs on different `m` → still
deterministic; reuse is impossible. If a pair of different `m`s shares `r` →
`ecdsa-nonce-reuse`. Else → gather ~`required_signatures` sigs for
`hnp-ecdsa` if `k` is bounded (check for timestamp/counter hints).

## "The DIY curve" — custom `p, a, b`

```
{"p": ..., "a": ..., "b": ..., "G": (x,y), "Q": (x,y), "ct": ...}
```

The defect ladder: `Δ == 0` → `singular_ec`; `#E == p` → `smart_attack`;
`#E` smooth → `pohlig-hellman` on the curve; `x` small → `bsgs`; else the
intended bug isn't dlog — look at the protocol.

## "The DH oracle" — a point-multiply service

```
POST /dh {"x": .., "y": ..}  →  {"shared": d·P'}
```

Submit an off-curve `P'` — accepted → invalid-curve; per fake curve `E'_i`
with smooth `ord(P'_i)`, recover `d mod ord(P'_i)`, CRT.

## "The JWT pair" — two signed tokens

```
header.payload.sig1   header.payload.sig2
```

`sig` is `r||s` raw (not DER in JWS). Same `r` → `ecdsa-nonce-reuse` → `d`
→ forge an admin JWT → flag.

## "The smooth modulus" — `h = g^x mod p`

`p-1` smooth → `pohlig-hellman`; else `x` bounded → `bsgs`.

## "The partial leak" — `k` bits in response

`sign` returns `{"r","s","k_low"}` or `k` masked → build `(t,u)` → `hnp`.

## The close

Every scenario ends `x·G == Q`/`g^x == h` then the flag step.

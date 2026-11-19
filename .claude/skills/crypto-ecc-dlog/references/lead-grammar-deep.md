# Lead grammar deep — every description cue → the route, expanded

## The nonce cues — the explicit ones

| Cue phrase | Route |
|---|---|
| "nonce"/"ephemeral key" | `k` is the target — scan `r`s, then bias checks |
| "reused"/"same r"/"twice" | `ecdsa-nonce-reuse` |
| "weak nonce"/"bad rng"/"predictable" | `hnp-ecdsa` (if bounded) or `crypto-prng` |
| "short nonce"/"128-bit nonce" | `hnp-ecdsa --nonce-bits 128` |
| "partial nonce"/"leaked bits"/"MSB"/"LSB" | `hnp` with `B` on unknown part |
| "timestamp"/"counter"/"unix time" | `hnp-ecdsa --nonce-bound <ts-range>` |
| "deterministic"/"RFC 6979" | reuse impossible on same `m`; cross-`m` only |

## The dlog cues — the explicit ones

| Cue phrase | Route |
|---|---|
| "discrete log"/"dlog"/"`g^x`" | `smoothness` gate → PH/BSGS |
| "smooth"/"factors of p-1"/"composite order" | `pohlig-hellman` |
| "small exponent"/"bounded"/"`x < N`" | `bsgs --order N` |
| "safe prime"/"modp"/"RFC 3526" | not dlog — protocol bug |
| "subgroup"/"`ord(g)`" | `smoothness --n ord(g)` |

## The curve cues — the explicit ones

| Cue phrase | Route |
|---|---|
| "elliptic curve"/"custom curve"/"DIY" | defect ladder — `Δ`/`#E`/smoothness |
| "anomalous"/"trace 1" | `smart_attack` (`#E == p` means trace `t=1`) |
| "singular"/"node"/"cusp"/"self-intersect" | `singular_ec` |
| "point"/"public key"/"`Q = d·G`" | curve verify shape |
| "DH"/"Diffie-Hellman"/"key agreement" | invalid curve (if unvalidated) |
| "secp256k1"/"P-256"/"NIST"/"Curve25519" | named curve → nonce attacks only |
| "pairing"/"bilinear"/"embedding" | MOV territory — flag, no tool |

## The format cues — the explicit ones

| Cue phrase | Route |
|---|---|
| "jwt"/"jws"/"token" | `ecdsa-nonce-reuse` if two share `r` |
| "DER"/"ASN.1" | normalize `(r,s)` ints first |
| "signature"/"signed" | nonce family |
| "certificate"/"pubkey"/"public key" | `d·G == Q` verify shape |
| "service"/"oracle"/"endpoint" | probe determinism + validation |

## The trap cues — the explicit ones

| Cue phrase | Route |
|---|---|
| "RSA"/"modulus"/"`n = pq`" | `crypto-rsa` — leave |
| "AES"/"CBC"/"GCM"/"XOR"/"keystream" | `crypto-symmetric-oracle` — leave |
| "random"/"predictable seed"/"PRNG" | `crypto-prng` — leave |
| "encode"/"base64"/"hex" | `misc-encoding-carrier` — leave |

# Lead grammar — the description cues → the route

## The nonce cues

| Cue | Route |
|---|---|
| "signature"/"sign"/"ECDSA" | nonce family — `r` scan first |
| "reused"/"same r"/"nonce" | `ecdsa-nonce-reuse` |
| "weak nonce"/"bad rng"/"short k" | `hnp-ecdsa` |
| "leaked bits"/"partial k" | `hnp`/`hnp-ecdsa` |
| "timestamp"/"counter" k | `hnp-ecdsa --nonce-bound` |

## The dlog cues

| Cue | Route |
|---|---|
| "discrete log"/"`g^x`" | `pohlig-hellman`/`bsgs` (smoothness first) |
| "smooth order"/"factors" | `pohlig-hellman` |
| "small exponent"/"bounded" | `bsgs` |
| "safe prime"/"modp" | likely not this — check for a different bug |

## The curve cues

| Cue | Route |
|---|---|
| "elliptic curve"/"custom curve" | defect family — `Δ`/`#E` checks |
| "anomalous" | `smart_attack` |
| "singular"/"node"/"cusp" | `singular_ec` |
| "DH"/"key agreement"/"multiplies your point" | invalid curve |
| "secp256k1"/"P-256"/"Curve25519" | real curve → nonce attacks |

## The format cues

| Cue | Route |
|---|---|
| "jwt"/"token" | `ecdsa-nonce-reuse` if two tokens share `r` |
| "DER" | normalize `(r,s)` ints first |
| "certificate"/"pubkey" | `d·G == Q` verify shape |

## The trap cues

| Cue | Route |
|---|---|
| "RSA"/"modulus" | `crypto-rsa` — leave |
| "AES"/"CBC"/"XOR" | `crypto-symmetric-oracle` — leave |
| "random"/"predictable" | `crypto-prng` — leave |

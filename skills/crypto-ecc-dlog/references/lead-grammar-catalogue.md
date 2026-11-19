# Lead grammar catalogue — every cue → the file that owns it

## The nonce cues → files

| Cue | Files |
|---|---|
| reuse/"same r" | `ecdsa-nonce-reuse*.md`,`lead-grammar*.md` |
| bias/"short k" | `hnp-ecdsa*.md`,`lead-grammar*.md` |
| leak/"MSB"/"LSB" | `hnp*.md`,`lead-grammar*.md` |
| "timestamp"/"counter" | `hnp-ecdsa-deep.md`,`scenarios*.md` |
| deterministic/RFC 6979 | `edge-cases-deep.md`,`theory*.md` |

## The dlog cues → files

| Cue | Files |
|---|---|
| "`g^x`"/"dlog" | `per-family-dlog.md`,`lead-grammar*.md` |
| smooth/"factors" | `pohlig-hellman*.md` |
| bounded/"small exponent" | `bsgs*.md` |
| safe prime/"modp" | `boundary-cases*.md`,`anti-patterns*.md` |

## The curve cues → files

| Cue | Files |
|---|---|
| "custom curve"/params | `per-family-curve-defect.md` |
| anomalous/"trace 1" | `smart-attack*.md` |
| singular/node/cusp | `singular-ec*.md` |
| DH/oracle | `invalid-curve*.md` |
| named curve | `per-family-nonce.md` |
| pairing | `per-family-curve-defect.md` |

## The format cues → files

| Cue | Files |
|---|---|
| jwt/jws | `scenarios*.md`,`lead-grammar*.md` |
| DER/ASN.1 | `edge-cases-deep.md` |
| oracle/endpoint | `recon-order*.md` |

## The trap cues → files

| Cue | Files |
|---|---|
| RSA/AES/PRNG/encode | `class-boundary*.md` |

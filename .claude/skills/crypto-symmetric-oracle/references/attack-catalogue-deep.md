# Attack catalogue — every route in the class — deep

| Attack | Needs | Distinguisher | Tool |
|---|---|---|---|
| ECB fingerprint | chosen plaintext | identical blocks | manual / ecb_oracle |
| Byte-at-a-time | encrypt(prefix‖secret) | block equality | `tools/ecb_oracle.py` |
| ECB cut-and-paste | block-structured token | field alignment | manual splice |
| CBC padding oracle | pad-valid vs pad-invalid | status/body/timing | `tools/pad_oracle.py` |
| CBC bit-flip | unauthenticated CBC | parser survives garbage | manual xor |
| IV=key | decrypt error echo | plaintext leak | 3-block algebra |
| CTR nonce reuse | same nonce 2× | P1 XOR P2 readable | `crib-drag` |
| Crib-drag | P1 XOR P2 + known word | plausible text | `crypto_attack.py crib-drag` |
| GCM nonce reuse | same nonce, 2 tagged records | tag algebra | `tools/gcm_nonce.py` |
| Length extension | sha1/sha256(secret‖m) | forged MAC accept | `crypto_attack.py length-extension` |
| Single-byte XOR | short ct, 1-byte key | printable decode | `crypto_attack.py single-byte-xor` |
| CBC-MAC splice | variable-len CBC-MAC | forged tag | manual splice |
| Tag truncation | partial-tag accept | shortened tag works | manual probe |
| Timing compare | early-exit == | timing split | manual loop |

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Attack | Needs | Distinguisher | Tool |
|---|---|---|---|
| ECB fingerprint | chosen plaintext | identical blocks | manual / ecb_oracle |
| Byte-at-a-time | encrypt(prefix‖secret) | block equality | `tools/ecb_oracle.py` |
| ECB cut-and-paste | block-structured token | field alignment | manual splice |
| CBC padding oracle | pad-valid vs pad-invalid | status/body/timing | `tools/pad_oracle.py` |
| CBC bit-flip | unauthenticated CBC | parser survives garbage | manual xor |
| IV=key | decrypt error echo | plaintext leak | 3-block algebra |
| CTR nonce reuse | same nonce 2× | P1 XOR P2 readable | `crib-drag` |
| Crib-drag | P1 XOR P2 + known word | plausible text | `crypto_attack.py crib-drag` |
| GCM nonce reuse | same nonce, 2 tagged records | tag algebra | `tools/gcm_nonce.py` |
| Length extension | sha1/sha256(secret‖m) | forged MAC accept | `crypto_attack.py length-extension` |
| Single-byte XOR | short ct, 1-byte key | printable decode | `crypto_attack.py single-byte-xor` |
| CBC-MAC splice | variable-len CBC-MAC | forged tag | manual splice |
| Tag truncation | partial-tag accept | shortened tag works | manual probe |
| Timing compare | early-exit == | timing split | manual loop |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`

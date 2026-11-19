# Field manual — one page per move — map

| Job | Tool |
|---|---|
| Byte-at-a-time ECB over HTTP | `tools/ecb_oracle.py` |
| CBC padding oracle over HTTP | `tools/pad_oracle.py` |
| GCM forbidden attack | `tools/gcm_nonce.py` |
| RSA parity oracle (boundary) | `tools/parity_oracle.py` |
| Crib-drag two same-keystream cts | `tools/crypto_attack.py crib-drag` |
| Length-extension forge | `tools/crypto_attack.py length-extension` |
| Single-byte XOR | `tools/crypto_attack.py single-byte-xor` |

Expanded rows and abort conditions: `field-manual.md` and `field-manual-deep.md`.

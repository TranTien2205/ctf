# Field manual — one page per move — deep



## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Job | Tool |
|---|---|
| Byte-at-a-time ECB over HTTP | `tools/ecb_oracle.py` |
| CBC padding oracle over HTTP | `tools/pad_oracle.py` |
| GCM forbidden attack | `tools/gcm_nonce.py` |
| RSA parity oracle (boundary) | `tools/parity_oracle.py` |
| Crib-drag two same-keystream cts | `tools/crypto_attack.py crib-drag` |
| Length-extension forge | `tools/crypto_attack.py length-extension` |
| Single-byte XOR | `tools/crypto_attack.py single-byte-xor` |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`

# Per-signal map — observation → the file that owns it — deep

| Signal | File |
|---|---|
| Identical ct blocks from repeated pt | `ecb-detection.md` |
| Deterministic output | `ecb-detection.md` / `encrypt-oracle-recon.md` |
| Block-step length growth | `detection.md` |
| 1:1 length growth | `ctr-nonce-reuse.md` / `stream-integrity.md` |
| Pad-vs-MAC error split | `cbc-padding-oracle.md` |
| Uniform reject for tampering | `authenticated-boundary.md` |
| Same nonce, two records | `ctr-nonce-reuse.md` / `gcm-nonce-reuse.md` |
| `hash(secret‖m)` in source | `length-extension.md` |
| hmac.new/HMAC( in source | `hmac-vs-raw-mac.md` |
| Short ct, 1-byte key shape | `single-byte-xor.md` |
| Verify endpoint, ok/invalid | `verify-oracle.md` |
| Decrypt echoes plaintext | `decrypt-oracle.md` |
| IV visible + fixed | `cbc-iv-equals-key.md` |
| Token = field-blocks | `ecb-cut-and-paste.md` |
| Timing split by position | `timing-oracles.md` |
| CRC-shaped 'MAC' | `mac-forgery.md` |
| Variable-len CBC-MAC | `cbc-mac.md` |
| Key/seed literal in handout | `key-path.md` |
| Compression in the chain | `boundary-cases.md` |
| Random prefix per request | `block-alignment.md` |

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Signal | File |
|---|---|
| Identical ct blocks from repeated pt | `ecb-detection.md` |
| Deterministic output | `ecb-detection.md` / `encrypt-oracle-recon.md` |
| Block-step length growth | `detection.md` |
| 1:1 length growth | `ctr-nonce-reuse.md` / `stream-integrity.md` |
| Pad-vs-MAC error split | `cbc-padding-oracle.md` |
| Uniform reject for tampering | `authenticated-boundary.md` |
| Same nonce, two records | `ctr-nonce-reuse.md` / `gcm-nonce-reuse.md` |
| `hash(secret‖m)` in source | `length-extension.md` |
| hmac.new/HMAC( in source | `hmac-vs-raw-mac.md` |
| Short ct, 1-byte key shape | `single-byte-xor.md` |
| Verify endpoint, ok/invalid | `verify-oracle.md` |
| Decrypt echoes plaintext | `decrypt-oracle.md` |
| IV visible + fixed | `cbc-iv-equals-key.md` |
| Token = field-blocks | `ecb-cut-and-paste.md` |
| Timing split by position | `timing-oracles.md` |
| CRC-shaped 'MAC' | `mac-forgery.md` |
| Variable-len CBC-MAC | `cbc-mac.md` |
| Key/seed literal in handout | `key-path.md` |
| Compression in the chain | `boundary-cases.md` |
| Random prefix per request | `block-alignment.md` |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`

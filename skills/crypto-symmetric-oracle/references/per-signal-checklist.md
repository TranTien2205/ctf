# Per-signal map — observation → the file that owns it — checklist

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

## Checklist

- [ ] check: Identical ct blocks from repeated pt
- [ ] check: Deterministic output
- [ ] check: Block-step length growth
- [ ] check: 1:1 length growth
- [ ] check: Pad-vs-MAC error split
- [ ] check: Uniform reject for tampering
- [ ] check: Same nonce, two records
- [ ] check: `hash(secret‖m)` in source
- [ ] check: hmac.new/HMAC( in source
- [ ] check: Short ct, 1-byte key shape
- [ ] check: Verify endpoint, ok/invalid
- [ ] check: Decrypt echoes plaintext
- [ ] check: IV visible + fixed
- [ ] check: Timing split by position
- [ ] check: CRC-shaped 'MAC'
- [ ] check: Variable-len CBC-MAC
- [ ] check: Key/seed literal in handout
- [ ] check: Compression in the chain
- [ ] check: Random prefix per request

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.

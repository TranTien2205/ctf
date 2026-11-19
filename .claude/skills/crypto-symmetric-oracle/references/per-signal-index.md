# Per-signal map — observation → the file that owns it — index

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

## Companions

- `per-signal-deep.md` — boundary conditions and the failure shape
- `per-signal-checklist.md` — the same content as an ordered checklist
- `per-signal-map.md` — the lookup table alone
- `../field-notes.md` — where outcomes land

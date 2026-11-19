# Byte-at-a-time ECB decryption — index

ECB + attacker-controlled prefix = an encryption oracle you can read secrets out of, one byte per position. The classic recipe: keep the secret's first unknown byte at the end of a controlled block, brute that byte through all 256 guesses, advance.

## Related modules

- `ecb-byte-at-a-time-deep.md` — mechanism internals and boundary conditions
- `ecb-byte-at-a-time-variant.md` — when the surface shape changes
- `ecb-byte-at-a-time-checklist.md` — the ordered operational steps
- `ecb-byte-at-a-time-catalogue.md` — case enumeration

## Cross-references

`ecb-detection.md` · `block-alignment.md` · `tools-ecb-oracle.md`

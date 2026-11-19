# Cryptopals map — this class, set by set — deep

The class IS most of cryptopals sets 1-3. The map is worth knowing because
CTF authors lift these exercises almost verbatim.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Challenge | Attack here |
|---|---|
| 1-3 single-byte XOR | `single-byte-xor.md` |
| 6 repeating-key XOR | `single-byte-xor.md` (keysize via Hamming) |
| 7 AES-ECB decrypt with key | key-path (decrypt directly) |
| 8 detect ECB in a batch | `ecb-detection.md` |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`

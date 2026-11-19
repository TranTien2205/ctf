# Format oracles vs padding oracles — deep

A 'padding oracle' is really a DECODE oracle: the check can be on any format,
not just PKCS#7. CTF authors exploit the assumption.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Check | Oracle question | Attack shape |
|---|---|---|
| PKCS#7 pad bytes | does it end in valid pad? | classic Vaudenay |
| JSON parse | does it decrypt to parseable JSON? | per-byte guess via parse error |
| Length field | is the decoded length sane? | 1-bit format oracle |
| Character whitelist | is it printable/ASCII? | per-byte narrowing |
| Checksum inside plaintext | does the inner CRC match? | chosen-ct format oracle |
| Ciphertext-stealing / CTS | does it parse + re-encrypt? | variant of Vaudenay |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`

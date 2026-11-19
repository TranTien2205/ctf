# Format oracles vs padding oracles — checklist

A 'padding oracle' is really a DECODE oracle: the check can be on any format,
not just PKCS#7. CTF authors exploit the assumption.

## Checklist

- [ ] check: PKCS#7 pad bytes
- [ ] check: JSON parse
- [ ] check: Length field
- [ ] check: Character whitelist
- [ ] check: Ciphertext-stealing / CTS

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.

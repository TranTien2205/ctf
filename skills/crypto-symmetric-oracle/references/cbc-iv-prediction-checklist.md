# CBC IV prediction — the BEAST-shaped case — checklist

When the IV for the NEXT message is predictable (chained from the previous
ciphertext block — the old TLS1.0 bug), chosen plaintext verifies guesses.

## Checklist

- [ ] IV_next = C_last of the previous message.
- [ ] To test whether a captured block decrypts to guess G: submit plaintext

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.

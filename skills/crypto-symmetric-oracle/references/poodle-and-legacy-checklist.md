# POODLE and the legacy TLS padding family — checklist

POODLE is the CBC padding oracle against SSL 3.0 / TLS CBC ciphersuites.
The same shape appears in CTF services that expose a TLS-like decrypt.

## Checklist

- [ ] check: PKCS#7 (app-layer)
- [ ] check: SSL3 POODLE
- [ ] check: TLS1.0 explicit IV
- [ ] check: Lucky13 timing

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.

# Multi-step chains — when one primitive isn't the flag — checklist

The flag is rarely one oracle call away. The standard chains:

## Checklist

- [ ] ecb-detection: confirm ECB + map field blocks.
- [ ] ecb-cut-and-paste: mint the 'admin' block from a chosen plaintext.
- [ ] token-forgery-workflows: splice, submit, read the privileged response.
- [ ] pre-flag the response bytes.

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.

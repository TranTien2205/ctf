# CMAC, OMAC, and the MAC-variant zoo — checklist

CBC-MAC's variable-length forgery was fixed by CMAC/OMAC: the last block is
XOR'd with a derived subkey before encryption, which kills the simple
splice. Naming the construction correctly is the whole game.

## Checklist

- [ ] Source names: `cmac`, `omacf`, `omac1`, `CBC_MAC`.
- [ ] Tag = 16 bytes, input variable-length, no per-message subkey field: CMAC

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.

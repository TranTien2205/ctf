# CBC IV = key and related IV bugs — case catalogue

If the service reuses the key as the IV (or exposes it through the decrypt error channel), three chosen-ciphertext queries recover the key. Rarer than padding oracles but instant when it fires.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Decryption errors echo raw plaintext back | error-channel oracle | key recovery in 3 blocks |
| 2 | Source shows iv = key or iv derived from key | IV=key construction | key recovery |
| 3 | IV predictable but independent (counter, timestamp) | predictable-IV chosen plaintext | verify guessed plaintext encryptions |

## Falsifier

Falsifier — the decrypt endpoint never echoes plaintext and the IV is random per message: no IV-equality signal exists. Drop to padding-oracle or reclassify.

## Coverage notes

- The classic exploit needs the service to SHOW you decrypted garbage — a silent decrypt gives nothing.
- Predictable-IV attacks need chosen plaintext and the ability to compare ciphertexts for equality — useless when each encryption is salted.

## Cross-references

`cbc-bitflip.md` · `cbc-padding-oracle.md`

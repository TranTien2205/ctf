# tools/parity_oracle.py — RSA bit-leak driver (boundary) — case catalogue

Drives a parity oracle over HTTP: each response tells whether the decrypted value is odd or even — used for RSA parity/LSB oracles. Listed here because it's an ORACLE shape, but it's RSA-class, not symmetric.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | --n --e --ct = RSA params | public key + ciphertext | RSA context |
| 2 | --url with {CT} | the oracle | the endpoint that decrypts |
| 3 | --ok-regex/--neg-regex = odd vs even answer | the distinguisher | measure first |
| 4 | --max-requests bounds the search | rate-limit bound | sized to the target |

## Falsifier

Falsifier — the oracle doesn't answer parity or the RSA params are wrong: no interval narrowing possible.

## Coverage notes

- This is RSA-parity/Bleichenbacher-family, not symmetric — don't confuse it with CBC padding.
- The regex polarity must match which response means odd vs even.

## Cross-references

`tools-pad-oracle.md` · `../crypto-rsa/`

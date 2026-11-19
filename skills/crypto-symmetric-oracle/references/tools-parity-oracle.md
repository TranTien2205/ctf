# tools/parity_oracle.py — RSA bit-leak driver (boundary)

Drives a parity oracle over HTTP: each response tells whether the decrypted value is odd or even — used for RSA parity/LSB oracles. Listed here because it's an ORACLE shape, but it's RSA-class, not symmetric.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --n --e --ct = RSA params | public key + ciphertext | RSA context |
| --url with {CT} | the oracle | the endpoint that decrypts |
| --ok-regex/--neg-regex = odd vs even answer | the distinguisher | measure first |
| --max-requests bounds the search | rate-limit bound | sized to the target |

## Steps

1. Confirm the oracle returns a parity-like answer (odd/even).
2. python3 tools/parity_oracle.py --n <n> --e <e> --ct <c> --url 'https://t/d?c={CT}' --ok-regex 'odd' --neg-regex 'even'.
3. The interval-halving loop runs itself; the message emerges bit by bit.
4. This is an RSA oracle — it belongs to crypto-rsa more than this class.

## Falsifier

Falsifier — the oracle doesn't answer parity or the RSA params are wrong: no interval narrowing possible.

## Traps

- This is RSA-parity/Bleichenbacher-family, not symmetric — don't confuse it with CBC padding.
- The regex polarity must match which response means odd vs even.

## Commands

```bash
python3 tools/parity_oracle.py --selftest
```

## Cross-references

`tools-pad-oracle.md` · `../crypto-rsa/`

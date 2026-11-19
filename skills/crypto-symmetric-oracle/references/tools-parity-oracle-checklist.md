# tools/parity_oracle.py — RSA bit-leak driver (boundary) — operational checklist

Drives a parity oracle over HTTP: each response tells whether the decrypted value is odd or even — used for RSA parity/LSB oracles. Listed here because it's an ORACLE shape, but it's RSA-class, not symmetric.

## Checklist

- [ ] Confirm the oracle returns a parity-like answer (odd/even).
- [ ] python3 tools/parity_oracle.py --n <n> --e <e> --ct <c> --url 'https://t/d?c={CT}' --ok-regex 'odd' --neg-regex 'even'.
- [ ] The interval-halving loop runs itself; the message emerges bit by bit.
- [ ] This is an RSA oracle — it belongs to crypto-rsa more than this class.

## Abort conditions

- This is RSA-parity/Bleichenbacher-family, not symmetric — don't confuse it with CBC padding.
- The regex polarity must match which response means odd vs even.

## Falsifier

Falsifier — the oracle doesn't answer parity or the RSA params are wrong: no interval narrowing possible.

## Cross-references

`tools-pad-oracle.md` · `../crypto-rsa/`

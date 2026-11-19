# Encrypt oracle reconnaissance — case catalogue

When the oracle encrypts what you give it, the surface is: what mode, what's prepended/appended, what's fixed. Map it before touching a tool.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Same input → same output | deterministic (ECB or fixed-IV) | ECB tests |
| 2 | Same input → different output | IV/nonce per request | nonce-reuse hunt |
| 3 | Output = encrypt(your_input + suffix) | suffix oracle | byte-at-a-time |
| 4 | Output = encrypt(prefix + your_input) | prefix oracle | alignment first |

## Falsifier

Falsifier — output is length-identical to input and non-deterministic under replay: it's a keystream, not a block cipher; route to ctr-nonce-reuse.

## Coverage notes

- 'Different output each time' can also be padding randomization — verify by diffing, not just length.
- A service that lowercases/escapes input before encrypting breaks byte-at-a-time prefix control.
- Base64'd output is 4/3 the ciphertext length — decode before measuring block size.

## Cross-references

`ecb-detection.md` · `block-alignment.md`

# Encrypt oracle reconnaissance

When the oracle encrypts what you give it, the surface is: what mode, what's prepended/appended, what's fixed. Map it before touching a tool.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Same input → same output | deterministic (ECB or fixed-IV) | ECB tests |
| Same input → different output | IV/nonce per request | nonce-reuse hunt |
| Output = encrypt(your_input + suffix) | suffix oracle | byte-at-a-time |
| Output = encrypt(prefix + your_input) | prefix oracle | alignment first |

## Steps

1. Determinism test: submit the same input twice — identical output means ECB or fixed-IV.
2. Length test: grow input; the output's step size is the block, the base is the fixed material length.
3. Structure test: submit varying-length repeated patterns to locate prefix/suffix boundaries.
4. Once the shape is named, route: ECB→byte-at-a-time/cut-paste, fixed-IV-CBC→IV tests, suffix→alignment.

## Falsifier

Falsifier — output is length-identical to input and non-deterministic under replay: it's a keystream, not a block cipher; route to ctr-nonce-reuse.

## Traps

- 'Different output each time' can also be padding randomization — verify by diffing, not just length.
- A service that lowercases/escapes input before encrypting breaks byte-at-a-time prefix control.
- Base64'd output is 4/3 the ciphertext length — decode before measuring block size.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
```

## Cross-references

`ecb-detection.md` · `block-alignment.md`

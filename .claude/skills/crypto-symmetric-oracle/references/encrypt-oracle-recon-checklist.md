# Encrypt oracle reconnaissance — operational checklist

When the oracle encrypts what you give it, the surface is: what mode, what's prepended/appended, what's fixed. Map it before touching a tool.

## Checklist

- [ ] Determinism test: submit the same input twice — identical output means ECB or fixed-IV.
- [ ] Length test: grow input; the output's step size is the block, the base is the fixed material length.
- [ ] Structure test: submit varying-length repeated patterns to locate prefix/suffix boundaries.
- [ ] Once the shape is named, route: ECB→byte-at-a-time/cut-paste, fixed-IV-CBC→IV tests, suffix→alignment.

## Abort conditions

- 'Different output each time' can also be padding randomization — verify by diffing, not just length.
- A service that lowercases/escapes input before encrypting breaks byte-at-a-time prefix control.
- Base64'd output is 4/3 the ciphertext length — decode before measuring block size.

## Falsifier

Falsifier — output is length-identical to input and non-deterministic under replay: it's a keystream, not a block cipher; route to ctr-nonce-reuse.

## Cross-references

`ecb-detection.md` · `block-alignment.md`

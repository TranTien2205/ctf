# Encrypt oracle reconnaissance — deep

When the oracle encrypts what you give it, the surface is: what mode, what's prepended/appended, what's fixed. Map it before touching a tool.

## Mechanism internals

The attack surface is defined by which byte the service lets you reach and which bit of the response leaks. The three invariants that hold across every variant of this attack: (1) the distinguisher must be measurable before the loop starts, (2) each recovered byte is confirmed by an exact-match answer — never a probabilistic one, (3) the loop stops at the measured boundary (block edge, secret length, tag width), not where the bytes 'look done'.

## Boundary conditions

- If the response is compressed before encryption, alignment dies — check for gzip/deflate first.
- If the oracle answers 'ok' for structurally invalid input, the parser layer is the bug, not the crypto.
- Rate limits convert a 40k-request loop into days — measure throughput and bound --max-requests.
- Nonce reuse at the block level is different from per-message reuse — align by absolute counter.
- A MAC checked before decryption closes every malleability route in this file.
- When the same tool flag is documented differently in two modules, tools/<name>.py --help is authoritative.

## Falsifier

Falsifier — output is length-identical to input and non-deterministic under replay: it's a keystream, not a block cipher; route to ctr-nonce-reuse.

## Highest-cost traps

- 'Different output each time' can also be padding randomization — verify by diffing, not just length.
- A service that lowercases/escapes input before encrypting breaks byte-at-a-time prefix control.
- Base64'd output is 4/3 the ciphertext length — decode before measuring block size.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
```

## Cross-references

`ecb-detection.md` · `block-alignment.md`

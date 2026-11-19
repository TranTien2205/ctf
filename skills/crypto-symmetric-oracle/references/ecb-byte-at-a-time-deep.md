# Byte-at-a-time ECB decryption — deep

ECB + attacker-controlled prefix = an encryption oracle you can read secrets out of, one byte per position. The classic recipe: keep the secret's first unknown byte at the end of a controlled block, brute that byte through all 256 guesses, advance.

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

Falsifier — the recovered plaintext stops being printable/structured partway through, or no candidate ever matches: the mode is not ECB or the 'secret' is encrypted separately (different key or different transform).

## Highest-cost traps

- Off-by-one at block boundaries: when your input is 0 mod block, the unknown byte is in the NEXT block — track absolute positions, not input length.
- A random per-request prefix defeats the method entirely; detect it by submitting the same input twice and diffing.
- PKCS#7: once you hit the pad region the oracle may reject un-pad-like guesses — stop at the measured secret length.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/profile?data={PTB}' --bs 16 --resp b64
python3 tools/ecb_oracle.py --url 'https://target/enc' --bs 16 --resp hex --max-requests 20000
```

## Cross-references

`ecb-detection.md` · `block-alignment.md` · `tools-ecb-oracle.md`

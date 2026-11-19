# Single-byte and repeating-key XOR — deep

A byte-XOR cipher is broken by frequency: try all 256 keys, score English-ness. Repeating-key XOR is the same problem after recovering key length by normalized Hamming distance.

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

Falsifier — no single-byte key produces mostly printable output AND the repeating-key analysis finds no keysize under ~40 that decodes coherently: the cipher is not XOR-with-short-key. Reclassify to classical or PRNG.

## Highest-cost traps

- Frequency scoring fails on <20-byte inputs — too little material; try known-structure cribs instead.
- Base64 the ciphertext BEFORE analysis if it arrived encoded — XOR'ing base64 text is the classic own-goal.
- Keysize multiples of the true keysize also score low; prefer the smallest plausible.

## Commands

```bash
python3 tools/crypto_attack.py single-byte-xor --ct <hex>
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
```

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`

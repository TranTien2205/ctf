# Oracle shapes — the four you can hold — deep

An oracle is any endpoint that answers a question about a ciphertext, a plaintext, or a tag. Before any exploit loop, name exactly which one you hold — encrypt, decrypt, padding-check, or verify — because the attack inventory differs completely per shape.

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

Falsifier — the service authenticates before decrypting (GCM tag, or HMAC verified first). A tampered ciphertext is rejected identically for every corruption; no oracle exists to query. Reclassify toward nonce reuse or key-material leaks instead.

## Highest-cost traps

- A 500-vs-200 pair is not automatically a padding oracle: compare invalid pad vs valid pad/invalid MAC first.
- Gzip/deflate before encryption destroys byte-at-a-time alignment — the ciphertext length stops tracking input length.
- A service that rate-limits at ~10 req/s cannot sustain a 40k-request padding loop; count request budget first.

## Commands

```bash
python3 tools/crypto_attack.py list
python3 tools/ecb_oracle.py --selftest
python3 tools/pad_oracle.py --selftest
```

## Cross-references

`ecb-detection.md` · `cbc-padding-oracle.md` · `ctr-nonce-reuse.md` · `mac-forgery.md` · `../field-notes.md`

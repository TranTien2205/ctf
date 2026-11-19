# ECB cut-and-paste / block substitution — deep

ECB blocks are independent: a ciphertext block decrypts the same wherever it sits. Forge a message by swapping, replaying, or re-ordering blocks — the standard target is role/admin fields in encrypted profiles.

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

Falsifier — the token carries a MAC over the whole ciphertext or the plaintext, or decrypt rejects spliced blocks: the construction is authenticated and cut-and-paste dies. Reclassify to mac-forgery or authenticated-boundary.

## Highest-cost traps

- Swapping two middle blocks corrupts NEITHER neighbor under ECB (unlike CBC) — that is the whole point; do not expect error signals.
- If the last block must survive PKCS#7 unpadding, your spliced block must end in valid pad bytes.
- Some services add a checksum block at the end — a splice then fails a CRC, not a MAC; a CRC is itself forgeable but differently.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
```

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md` · `token-forgery-workflows.md`

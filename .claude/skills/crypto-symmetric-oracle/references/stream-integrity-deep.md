# Stream/CTR integrity — malleability — deep

CTR/stream ciphertext is malleable per-bit: flip a ciphertext bit and the same plaintext bit flips. No integrity means you own the plaintext.

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

Falsifier — the ciphertext carries a MAC over it: malleation is rejected. Reclassify to mac-forgery or authenticated-boundary.

## Highest-cost traps

- Unlike CBC, NO garbage block is produced — the edit is invisible at the crypto layer.
- The plaintext offset you flip must exist — a 10-byte field at offset 200 can't be reached if the message is 100 bytes.
- Ciphertext-only edits don't need a decrypt endpoint — the service's own use of the plaintext is the attack.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h> --ct2 <h> --crib '<known>'
```

## Cross-references

`ctr-nonce-reuse.md` · `cbc-bitflip.md` · `token-forgery-workflows.md`

# Key path — leaked, weak, or derived keys — deep

Sometimes the crypto is honest and the key isn't: hardcoded keys, weak seeds, derived-from-timestamp keys, keys in the handout. Check before building an oracle loop.

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

Falsifier — no key material leaks and the KDF is honest: the key path is closed. Proceed to oracle attacks.

## Highest-cost traps

- A 'key' that's actually a password still needs the right KDF to become a key.
- Keys derived from non-cryptographic PRNG state belong to crypto-prng, not this class.
- Encrypted key files with weak passphrases are a cracking problem (hashcat/john), not an oracle problem.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`authenticated-boundary.md` · `../crypto-prng/`

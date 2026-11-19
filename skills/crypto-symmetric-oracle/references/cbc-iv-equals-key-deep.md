# CBC IV = key and related IV bugs — deep

If the service reuses the key as the IV (or exposes it through the decrypt error channel), three chosen-ciphertext queries recover the key. Rarer than padding oracles but instant when it fires.

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

Falsifier — the decrypt endpoint never echoes plaintext and the IV is random per message: no IV-equality signal exists. Drop to padding-oracle or reclassify.

## Highest-cost traps

- The classic exploit needs the service to SHOW you decrypted garbage — a silent decrypt gives nothing.
- Predictable-IV attacks need chosen plaintext and the ability to compare ciphertexts for equality — useless when each encryption is salted.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h> --ct2 <h> --crib 'flag{'
```

## Cross-references

`cbc-bitflip.md` · `cbc-padding-oracle.md`

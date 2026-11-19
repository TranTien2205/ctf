# CBC-MAC and MAC-construction flaws — deep

CBC-MAC is secure for fixed-length messages and forgeable for variable-length ones. A CTF classic: given MAC(m), produce MAC(m || m' ) without the key.

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

Falsifier — the MAC is CMAC/HMAC or prepends the length safely: the splice is rejected. Reclassify to length-extension or mac-forgery.

## Highest-cost traps

- CBC-MAC splices need a known (m, t) pair — request one first.
- The patch bytes are XOR'd into the first block of the extension — they must parse in the message format.
- This is NOT hash length-extension: CBC-MAC is a block cipher construction; don't confuse the two tools.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`mac-forgery.md` · `length-extension.md`

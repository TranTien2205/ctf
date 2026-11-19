# crib-drag driver — XOR two same-keystream ciphertexts — deep

tools/crypto_attack.py crib-drag slides your guessed word across the XOR of two ciphertexts and prints every offset where it yields plausible text on both sides.

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

Falsifier — no offset ever yields printable on both sides: the keystreams differ (different nonces) or the data is compressed/binary.

## Highest-cost traps

- The crib must match case and exact bytes — 'flag{' not 'FLAG{'.
- Two printable chars XOR to something non-printable; a hit shows the OTHER side's text, not both.
- Spaces reveal letters via case-flip; run a space crib too.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib ' the '
```

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`

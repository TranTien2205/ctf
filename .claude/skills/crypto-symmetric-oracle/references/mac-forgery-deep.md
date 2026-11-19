# MAC and tag forgery — the non-extension routes — deep

When length-extension does not apply, forgery still exists: tag truncation, verification via == (timing compare), unkeyed checksums labeled 'MAC', and key-confusion between verify and sign.

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

Falsifier — the tag is verified in constant time, at full length, under a real MAC: forgery reduces to 2^-n luck, which is not an attack. Reclassify toward the key path.

## Highest-cost traps

- Timing attacks on tags need MANY samples per byte — noise swamps a 1ns difference; measure the channel first.
- A truncated tag with only 2-3 accepted bytes is still 16-24 bits of brute force — feasible but bound it first.
- CRC patch bytes go at a position the parser tolerates — usually the end or a length field.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`hmac-vs-raw-mac.md` · `length-extension.md` · `authenticated-boundary.md`

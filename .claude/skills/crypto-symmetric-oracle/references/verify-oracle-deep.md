# Verify oracle — tag checking as a distinguisher — deep

A verify endpoint that answers 'tag good' vs 'tag bad' is an oracle on the authentication side. Timing in the compare function, truncation, and acceptance of malformed tags all leak.

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

Falsifier — the verify is constant-time, full-length, type-strict: no oracle. Reclassify toward key-path or different class.

## Highest-cost traps

- Timing measurement needs MANY samples (50+) and baseline correction — a single diff proves nothing.
- Truncation acceptance is a bug, not an attack: it only helps if you still have to produce the accepted prefix.
- Parser-level accepts (None, '') sometimes bypass the check entirely — always try the trivial cases first.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`mac-forgery.md` · `response-distinguishers.md`

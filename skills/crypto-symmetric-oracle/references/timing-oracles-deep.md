# Timing oracles — when time is the only channel — deep

When status and body are identical, timing remains. It works but it's fragile: jitter, warmup, and load can all masquerade as signal.

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

Falsifier — even with 200+ samples, the two distributions overlap completely: no timing oracle. Reclassify.

## Highest-cost traps

- A 1-byte-early exit difference is ~1ns — invisible over the network; only macro differences (crypto ops, sleeps) survive.
- Load on the target destroys timing signal — measure when quiet.
- Warmup: the first request is always different — discard it.

## Commands

```bash
python3 tools/pad_oracle.py --ct <h> --url 'https://t/d?c={CT}' --ok-regex 'ok'
```

## Cross-references

`response-distinguishers.md` · `cbc-padding-oracle.md`

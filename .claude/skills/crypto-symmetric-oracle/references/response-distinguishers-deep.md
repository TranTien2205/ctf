# Response distinguishers — what counts as an oracle signal — deep

A padding oracle needs TWO distinguishable answers. Enumerate the channels: status, body text, length, timing, connection behavior. Document the distinguisher BEFORE running the loop.

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

Falsifier — every corruption produces an identical answer across all channels, including averaged timing: no oracle exists.

## Highest-cost traps

- Error text that LOOKS different but comes from the HTTP framework (not the crypto layer) is still a valid distinguisher — use it.
- Timing-only oracles are fragile: warmup, jitter, and averaging are mandatory; 5 samples is not a measurement.
- A catch-all error page with identical body but different CONTENT-LENGTH is still distinguishable.

## Commands

```bash
python3 tools/pad_oracle.py --ct <h> --url 'https://t/d?c={CT}' --ok-regex 'OK'
```

## Cross-references

`cbc-padding-oracle.md` · `tools-pad-oracle.md`

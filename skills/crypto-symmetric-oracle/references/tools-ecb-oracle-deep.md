# tools/ecb_oracle.py — the byte-at-a-time driver — deep

The sanctioned HTTP driver for byte-at-a-time ECB: it holds request and response together, runs the guess loop, and emits the post-probe command shape hooks.py wants.

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

Falsifier — no candidate byte ever matches: either not ECB, or the response format flag is wrong, or the injection point doesn't reach the encrypt call. Verify the URL template first.

## Highest-cost traps

- {PT} vs {PTB}: hex doubles length, base64 adds padding — the service must accept whichever you pick.
- --resp raw is almost never right over HTTP — prefer hex/b64.
- --max-requests default may exceed the target's rate limit — measure first.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
python3 tools/ecb_oracle.py --url 'https://t/e?d={PTB}' --bs 16 --resp b64
```

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-detection.md`

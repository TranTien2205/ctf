# CBC padding oracle — Vaudenay decryption — deep

A service that answers 'padding valid' vs 'padding invalid' decrypts arbitrary ciphertext for you, one byte per ~256 requests. The error channel IS the exploit.

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

Falsifier — every corruption returns byte-identical responses (status, body, AND timing within noise): no oracle exists. An HMAC checked before decryption produces exactly this signature.

## Highest-cost traps

- Timing CAN be the distinguisher when statuses match — but you need many samples and a stable measure; prefer body/status signals.
- The false-positive at the last byte (\x01 vs a longer real pad) is the classic bug — always re-verify with a second byte change.
- Some services return 200 with an error body — --ok-regex on body text, not --ok-status.

## Commands

```bash
python3 tools/pad_oracle.py --ct <hex-ct-with-iv> --url 'https://target/dec?ct={CT}' --ok-regex 'OK|accepted'
python3 tools/pad_oracle.py --selftest
```

## Cross-references

`tools-pad-oracle.md` · `response-distinguishers.md` · `cbc-bitflip.md`

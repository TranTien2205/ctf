# tools/parity_oracle.py — RSA bit-leak driver (boundary) — deep

Drives a parity oracle over HTTP: each response tells whether the decrypted value is odd or even — used for RSA parity/LSB oracles. Listed here because it's an ORACLE shape, but it's RSA-class, not symmetric.

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

Falsifier — the oracle doesn't answer parity or the RSA params are wrong: no interval narrowing possible.

## Highest-cost traps

- This is RSA-parity/Bleichenbacher-family, not symmetric — don't confuse it with CBC padding.
- The regex polarity must match which response means odd vs even.

## Commands

```bash
python3 tools/parity_oracle.py --selftest
```

## Cross-references

`tools-pad-oracle.md` · `../crypto-rsa/`

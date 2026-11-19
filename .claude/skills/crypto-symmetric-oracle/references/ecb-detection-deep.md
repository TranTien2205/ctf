# ECB detection — one request, deterministic — deep

ECB leaks structure: identical plaintext blocks produce identical ciphertext blocks. Detection needs one request holding enough repeated material to fill two blocks — no statistical test, no second round-trip.

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

Falsifier — no duplicated 16-byte window appears anywhere in a 48-byte repeated input after ruling out misalignment, and the length grows continuously rather than in block steps: the mode is not ECB.

## Highest-cost traps

- A fixed server-side prefix shifts your alignment; the duplicate blocks appear offset by prefix_len mod 16.
- CBC with a fixed IV can mimic ECB on the FIRST block only — check pairs past offset 0.
- Compression before encryption makes 'A'*48 compress to nothing — no duplicate ever appears; that is a different challenge (CRIME-style).

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
python3 tools/ecb_oracle.py --selftest
```

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-cut-and-paste.md` · `block-alignment.md`

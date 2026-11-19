# ECB prefix vs suffix oracles — deep

Byte-at-a-time works when your input PRECEDES the secret (suffix). When the secret precedes your input, the method inverts — recover backwards, or via a fixed suffix oracle.

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

Falsifier — neither prefix nor suffix is controllable (your input is wholly inside fixed material): the oracle doesn't reach the secret.

## Highest-cost traps

- A random per-request prefix only defeats alignment, not the method — if a fixed suffix exists, attack backwards.
- Prefix recovery is rarer; double-check your orientation before implementing.
- Multiple secrets in one ciphertext can be independent — measure each region separately.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
```

## Cross-references

`ecb-byte-at-a-time.md` · `block-alignment.md`

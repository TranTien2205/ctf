# Block alignment — prefix, suffix, boundary math — deep

Every ECB/ECB-CBC trick lives or dies on alignment: where the service's fixed prefix ends and your controllable block boundary begins. Measure it before building any guess block.

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

Falsifier — no input length ever produces two adjacent identical blocks: there is no ECB region reachable, the mode is not ECB, or compression precedes encryption.

## Highest-cost traps

- Padding under PKCS#7 adds a full block when input ≡ 0 (mod block) — alignment math must include the pad block.
- URL-safe base64 of the ciphertext shifts byte positions by 4/3 — always measure on decoded bytes.
- A prefix that changes per-request but is constant within a request still lets cut-and-paste work once the length is measured per-request.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
```

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md`

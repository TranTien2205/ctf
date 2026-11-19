# ECB block reordering — structure-aware splicing — deep

Beyond cut-and-paste: reordering, deleting, and duplicating ECB blocks while keeping the whole token well-formed. Useful when only partial fields are reachable by direct substitution.

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

Falsifier — tokens carry a whole-message MAC or integrity check; reordering is detected. Reclassify.

## Highest-cost traps

- A count/length field elsewhere in the token must match the new block count.
- Reordering mid-token can desync per-record checksums inside the plaintext.
- Duplicating a block is undetectable unless there's a sequence field — check for one.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
```

## Cross-references

`ecb-cut-and-paste.md` · `token-forgery-workflows.md`

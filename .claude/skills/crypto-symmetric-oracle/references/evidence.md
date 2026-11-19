# Evidence discipline for oracle challenges

The oracle is a claim about a response channel. Evidence = the two responses
that differ, quoted verbatim.

## What counts as a confirm

| Stage | Evidence | post-probe kind |
|---|---|---|
| ECB fingerprint | two identical ciphertext blocks from repeated input | class |
| Padding-vs-MAC split | both responses verbatim | class |
| Nonce reuse | the two captured records with the same nonce | class |
| Forged tag accepted | the verify response | impact |
| Flag in response | the live response bytes | flag via pre-flag |

## Commands

```bash
python3 tools/hooks.py post-probe <challenge> --verdict confirms \
  --hypothesis-id <id> --class crypto-symmetric-oracle \
  --evidence-kind class \
  --evidence 'identical blocks at offset 32,48: 9f2c...' \
  --response '<the bytes the evidence was read from>'
```

```bash
python3 tools/hooks.py pre-flag <challenge> \
  --value 'flag{...}' \
  --evidence '<the response/artifact bytes it was read from>'
```

## What does NOT count

- A plausible-looking error — must differ from the OTHER corruption's error.
- A timing guess — must survive 50+ samples on both sides.
- A flag-shaped string typed into the request — only a response carries it.
- "The ciphertext looks random" — no oracle signal either way.

## Negative results

Record what was ruled out with the measurement: 'no identical block in
48-byte repeated input' closes ECB; 'uniform reject for all corruption
offsets' closes the class. These go to `../field-notes.md`.

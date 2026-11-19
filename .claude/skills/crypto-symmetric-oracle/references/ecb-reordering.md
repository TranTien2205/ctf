# ECB block reordering — structure-aware splicing

Beyond cut-and-paste: reordering, deleting, and duplicating ECB blocks while keeping the whole token well-formed. Useful when only partial fields are reachable by direct substitution.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Token has repeated structure (list of records) | block reordering applies | re-order the record blocks |
| Field you need exists only in OTHER tokens | block transplant | harvest across tokens |
| Trailing block must remain a valid pad | last block constraints | plan splice so pad survives |

## Steps

1. Enumerate which ciphertext blocks correspond to which logical fields/records.
2. Harvest: collect blocks from chosen-plaintext tokens that carry the values you need.
3. Assemble the forged token so field positions, count fields, and pad all remain consistent.
4. Verify: submit the forged token — a clean parse with the intended field is the confirm.

## Falsifier

Falsifier — tokens carry a whole-message MAC or integrity check; reordering is detected. Reclassify.

## Traps

- A count/length field elsewhere in the token must match the new block count.
- Reordering mid-token can desync per-record checksums inside the plaintext.
- Duplicating a block is undetectable unless there's a sequence field — check for one.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
```

## Cross-references

`ecb-cut-and-paste.md` · `token-forgery-workflows.md`

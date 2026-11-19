# ECB block reordering — structure-aware splicing — case catalogue

Beyond cut-and-paste: reordering, deleting, and duplicating ECB blocks while keeping the whole token well-formed. Useful when only partial fields are reachable by direct substitution.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Token has repeated structure (list of records) | block reordering applies | re-order the record blocks |
| 2 | Field you need exists only in OTHER tokens | block transplant | harvest across tokens |
| 3 | Trailing block must remain a valid pad | last block constraints | plan splice so pad survives |

## Falsifier

Falsifier — tokens carry a whole-message MAC or integrity check; reordering is detected. Reclassify.

## Coverage notes

- A count/length field elsewhere in the token must match the new block count.
- Reordering mid-token can desync per-record checksums inside the plaintext.
- Duplicating a block is undetectable unless there's a sequence field — check for one.

## Cross-references

`ecb-cut-and-paste.md` · `token-forgery-workflows.md`

# ECB block reordering — structure-aware splicing — operational checklist

Beyond cut-and-paste: reordering, deleting, and duplicating ECB blocks while keeping the whole token well-formed. Useful when only partial fields are reachable by direct substitution.

## Checklist

- [ ] Enumerate which ciphertext blocks correspond to which logical fields/records.
- [ ] Harvest: collect blocks from chosen-plaintext tokens that carry the values you need.
- [ ] Assemble the forged token so field positions, count fields, and pad all remain consistent.
- [ ] Verify: submit the forged token — a clean parse with the intended field is the confirm.

## Abort conditions

- A count/length field elsewhere in the token must match the new block count.
- Reordering mid-token can desync per-record checksums inside the plaintext.
- Duplicating a block is undetectable unless there's a sequence field — check for one.

## Falsifier

Falsifier — tokens carry a whole-message MAC or integrity check; reordering is detected. Reclassify.

## Cross-references

`ecb-cut-and-paste.md` · `token-forgery-workflows.md`

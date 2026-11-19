# Detection — naming the oracle in ≤5 requests — map

| 1 | 2 | 3 | 4 | 5 | Route |
|---|---|---|---|---|---|
| same | block | repeat | — | no tag | ECB |
| same | block | none | 2 answers | no tag | CBC padding oracle |
| diff | 1:1 | — | — | no tag | CTR/stream |
| diff | block | none | 2 answers | tag-after | CBC + tag (weird) |
| — | — | — | uniform | tag-before | authenticated boundary |

Expanded rows and abort conditions: `detection.md` and `detection-deep.md`.

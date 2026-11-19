# Detection — naming the oracle in ≤5 requests — deep

The discriminator runs once, before any exploit. Five probes, each cheap,
each ruling out a branch.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| 1 | 2 | 3 | 4 | 5 | Route |
|---|---|---|---|---|---|
| same | block | repeat | — | no tag | ECB |
| same | block | none | 2 answers | no tag | CBC padding oracle |
| diff | 1:1 | — | — | no tag | CTR/stream |
| diff | block | none | 2 answers | tag-after | CBC + tag (weird) |
| — | — | — | uniform | tag-before | authenticated boundary |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`

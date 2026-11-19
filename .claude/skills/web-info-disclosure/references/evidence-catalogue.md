# Evidence — disclosure proofs — case catalogue

A disclosure finding's evidence is the artifact itself, verbatim. post-probe records the excerpt; pre-flag only on response bytes.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | The artifact content itself | proof | post-probe class evidence |
| 2 | The recovered repo/source | impact when it leads somewhere | chain to sink |
| 3 | Catch-all baseline diff | the discriminator | record in notes |

## Falsifier

--

## Coverage notes

- A catch-all 200 is NOT a finding — the content must differ from baseline.
- Tool output alone isn't evidence; the response bytes are.

## Cross-references

`catchall-falsifier.md`

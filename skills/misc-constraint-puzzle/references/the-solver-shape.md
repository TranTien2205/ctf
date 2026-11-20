# The solver's shape — three functions

`parse(bytes) -> question`, `solve(question) -> answer`,
`format(answer) -> bytes` — keep them separate so a format drift
touches only the parser.

## Three functions

parse/solve/format — drift touches one.

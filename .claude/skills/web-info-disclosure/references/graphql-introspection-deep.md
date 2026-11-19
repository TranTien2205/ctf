# GraphQL introspection — schema disclosure — deep

Introspection returns the entire schema — types, queries, mutations — the route map AND the data model.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no GraphQL endpoint or introspection and errors are both silent: channel closed.

## Highest-cost traps

- Introspection off doesn't block attacks — suggestions via error messages continue.
- The schema names mutations — write operations are in web-graphql's depth.

## Commands

```bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"{__schema{types{name}}}"}' '$BASE/graphql'
```

## Cross-references

`api-docs-exposure.md` · `../web-graphql/`

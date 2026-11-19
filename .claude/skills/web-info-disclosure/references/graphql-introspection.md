# GraphQL introspection — schema disclosure

Introspection returns the entire schema — types, queries, mutations — the route map AND the data model.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| introspection query returns schema | full schema | hands to web-graphql |
| introspection 403 but schema guessable | partial | field fuzzing (different class) |
| __schema/__type in responses | GraphQL confirmed | web-graphql |

## Steps

1. POST the introspection query to /graphql or the discovered endpoint.
2. A full schema response is the disclosure — every query/mutation is now known.
3. If introspection is off, the endpoint still leaks via error messages (field suggestions).
4. Schema abuse is web-graphql's class — disclosure ends at the schema.

## Falsifier

Falsifier — no GraphQL endpoint or introspection and errors are both silent: channel closed.

## Traps

- Introspection off doesn't block attacks — suggestions via error messages continue.
- The schema names mutations — write operations are in web-graphql's depth.

## Commands

```bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"{__schema{types{name}}}"}' '$BASE/graphql'
```

## Cross-references

`api-docs-exposure.md` · `../web-graphql/`

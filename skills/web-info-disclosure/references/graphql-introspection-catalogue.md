# GraphQL introspection — schema disclosure — case catalogue

Introspection returns the entire schema — types, queries, mutations — the route map AND the data model.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | introspection query returns schema | full schema | hands to web-graphql |
| 2 | introspection 403 but schema guessable | partial | field fuzzing (different class) |
| 3 | __schema/__type in responses | GraphQL confirmed | web-graphql |

## Falsifier

Falsifier — no GraphQL endpoint or introspection and errors are both silent: channel closed.

# GraphQL introspection — schema disclosure — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| introspection query returns schema | full schema | hands to web-graphql |
| introspection 403 but schema guessable | partial | field fuzzing (different class) |
| __schema/__type in responses | GraphQL confirmed | web-graphql |

## Falsifier

Falsifier — no GraphQL endpoint or introspection and errors are both silent: channel closed.

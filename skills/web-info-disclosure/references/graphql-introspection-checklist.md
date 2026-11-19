# GraphQL introspection — schema disclosure — checklist

Introspection returns the entire schema — types, queries, mutations — the route map AND the data model.

## Checklist

- [ ] POST the introspection query to /graphql or the discovered endpoint.
- [ ] A full schema response is the disclosure — every query/mutation is now known.
- [ ] If introspection is off, the endpoint still leaks via error messages (field suggestions).
- [ ] Schema abuse is web-graphql's class — disclosure ends at the schema.

## Abort conditions

- Introspection off doesn't block attacks — suggestions via error messages continue.
- The schema names mutations — write operations are in web-graphql's depth.

## Falsifier

Falsifier — no GraphQL endpoint or introspection and errors are both silent: channel closed.

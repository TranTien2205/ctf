# API docs and schema exposure — operational checklist

Swagger/OpenAPI, GraphQL introspection, and generated API docs hand you the complete endpoint map plus parameter shapes — the cheapest route map available.

## Checklist

- [ ] Probe: /swagger.json /openapi.json /api-docs /v3/api-docs /graphql.
- [ ] Parse the spec: every path, method, and parameter is now known — the fuzz surface.
- [ ] Flag admin/internal/debug routes in the spec for priority probing.
- [ ] GraphQL introspection → hand to web-graphql for schema abuse.

## Abort conditions

- A docs UI page is HTML; find the spec URL it loads (usually in the page source).
- Private/internal operations may need auth even in the spec — listed is not callable.
- Old spec versions may persist at versioned paths (/v1/ when the API is v3).

## Falsifier

Falsifier — no spec endpoints exist and the API surface is small and self-evident: nothing hidden was disclosed.

## Cross-references

`exposed-artifacts.md` · `../web-graphql/`

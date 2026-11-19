# API docs and schema exposure — deep

Swagger/OpenAPI, GraphQL introspection, and generated API docs hand you the complete endpoint map plus parameter shapes — the cheapest route map available.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — no spec endpoints exist and the API surface is small and self-evident: nothing hidden was disclosed.

## Highest-cost traps

- A docs UI page is HTML; find the spec URL it loads (usually in the page source).
- Private/internal operations may need auth even in the spec — listed is not callable.
- Old spec versions may persist at versioned paths (/v1/ when the API is v3).

## Commands

```bash
for p in /swagger.json /openapi.json /api-docs /graphql; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`exposed-artifacts.md` · `../web-graphql/`

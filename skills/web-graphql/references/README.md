# web-graphql — reference index

Deep reference for GraphQL abuse. Every file exists; the order is the order
to read them in.

---

## Routing order

1. **`detection.md`** — find the endpoint, confirm GraphQL, fingerprint the engine.
2. **`introspection.md`** — the canonical `__schema` pull + degraded variants.
3. **`schema-analysis.md`** — the type list → attack table.
4. **`workflow.md`** — the bounded end-to-end methodology.
5. **`ctf-shapes.md`** — the shape catalogue: name → play.
6. **`ctf-walkthroughs.md`** — the solved-writeup recipes.

## Discovery when introspection is off

- **`introspection-off.md`** — suggestion oracle, `__type` side-channel,
  `_service{sdl}`, bundle mining, WS channel.
- **`wordlists.md`** — the seed names for `map --seed`.
- **`payload-dictionary.md` §21** — the introspection-off probe set.

## Per-bug-class depth

- **`idor-graphql.md`** — object reads, `node()`/`_entities`, nested escapes.
- **`authz-bypass.md`** — the 7 bypass shapes + two-role differential.
- **`node-interface.md`** — Relay `node(id)`/`nodes(ids:)` deep dive.
- **`federation.md`** — gateway/subgraph/`_entities`/`_service` attacks.
- **`injection-graphql.md`** — SQLi/NoSQLi/cmdi/ssti/ssrf/lfi through args.
- **`type-confusion.md`** — coercion, ID canonicalization, JSON-scalar objects.
- **`mutation-abuse.md`** — mass-assign, privesc, second-order, race.
- **`file-upload-graphql.md`** — the multipart spec + upload sinks.
- **`subscriptions.md`** — the WS channel, CSWSH, subscription authz.
- **`csrf-graphql.md`** — transport carriers and the CSRF matrix.
- **`blind-graphql.md`** — boolean/timing/length oracles when data is suppressed.
- **`second-order.md`** — stored payloads, deferred renders, blind triggers.
- **`directives-deep.md`** — `@skip`/`@include`, `@defer`/`@stream`, custom authz.
- **`persisted-queries.md`** — APQ and allowlist bypasses.
- **`graphql-over-http.md`** — the transport contract: methods, CTs, shapes.

## Per-engine depth

- **`framework-notes.md`** — Apollo, yoga, graphene, Hasura, java, ruby,
  absinthe, hotchocolate, juniper, mercurius, gqlgen, lighthouse, postgraphile.
- **`hasura.md`** — role-based authz, header spoofing, `_regex` extraction.

## Corpus

- **`payload-dictionary.md`** — the categorized query corpus (~500 payloads).
- **`payload-dictionary-2.md`** — type-confusion + variables + directives (~550).
- **`wordlists.md`** — the field-name seed corpus (~600 names).

## Working files

- **`evidence-rules.md`** — what proves what; the verdict ladder.
- **`denied-conditions.md`** — the falsifiers that close the class.
- **`common-mistakes.md`** — the 30 failure modes.
- **`error-analysis.md`** — the `errors` array anatomy.
- **`tooling.md`** — `graphql_probe`/`http_probe`/`oob_listener`/`bundle_miner`
  verified usage.
- **`waf-bypass.md`** — transport/document/content-level bypasses.
- **`writeup-techniques.md`** — the provenance corpus (writeup URLs + verbatim).

## Cross-skill routes

| The bug is really | Open |
|---|---|
| object read | `skills/web-idor/` |
| SQL/NoSQL via arg | `skills/web-sqli/` / `skills/web-nosqli/` |
| cmd via arg | `skills/web-command-injection/` |
| template via arg | `skills/web-ssti/` |
| URL fetch via arg | `skills/web-ssrf/` |
| file path via arg | `skills/file-read-primitives/` |
| upload sink | `skills/web-file-upload/` |
| session token | `skills/web-auth-session/` |
| stored XSS | `skills/web-xss/` |
| CSRF via transport | `skills/web-csrf/` / `skills/web-cors/` |
| mass assignment | `skills/web-mass-assignment/` |
| WS channel | `skills/web-websocket/` |
| prototype pollution | `skills/web-prototype-pollution/` |
| race via mutation | `skills/web-race-condition/` |

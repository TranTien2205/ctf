# GraphQL surface — mining the client for the schema hints

## The GraphQL endpoint

A bundle that calls a GraphQL API names the endpoint — `/graphql`,
`/api/graphql`, `/gql`, `/query`. Finding it routes to `web-graphql`.

```bash
grep -oE '"/?(graphql|gql|query|api/graphql)"' bundle.js | sort -u
grep -oE '(fetch|axios)\.(post)?\(["'"'"'`][^"'"'"'`]*graphql' bundle.js
```

## The query/mutation strings

The client's queries are in the bundle as strings — they name the
schema's fields, arguments, and types:

```bash
# query/mutation/subscription strings
grep -oE '(query|mutation|subscription)\s+[A-Za-z_]+\s*\([^)]*\)\s*\{' bundle.js | sort -u
grep -oE '\{\s*[a-zA-Z_]+\s*(\([^)]*\))?\s*\{[^}]+\}' bundle.js | head -30
# field names the client requests
grep -oE '\b(user|users|admin|secret|flag|internal|config|token|file|query|mutation)\s*(\([^)]*\))?\s*\{' bundle.js | sort -u
```

## The fragment/type names

`fragment X on Y`, `type`, `... on Z` — the schema's type and field
names, a pre-introspection map:

```bash
grep -oE 'fragment\s+[A-Za-z_]+\s+on\s+[A-Za-z_]+' bundle.js | sort -u
grep -oE '\.\.\.\s*on\s+[A-Za-z_]+' bundle.js | sort -u
grep -oE 'type\s*=\s*"[A-Z][a-zA-Z_]+"' bundle.js
```

## The interesting field hunt

The client's own queries may reference `admin`, `secret`, `flag`,
`internal`, `config`, `users` — fields the UI does not expose but the
schema has. A field name in a client query is a direct `web-graphql`
probe.

## The persisted-query / operation-name surface

`operationName`, `persistedQuery`, `extensions` — a persisted-query
setup where the operation name is the key:

```bash
grep -oE '(operationName|persistedQuery|extensions)\s*:\s*["'"'"']?[A-Za-z_]+' bundle.js | sort -u
```

## The route

A GraphQL endpoint + a field map → `web-graphql` for the introspection
and abuse. The bundle's queries are the schema hints `web-graphql`
would otherwise introspect for.

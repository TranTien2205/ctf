# Mining notes — what the writeup corpus teaches

The 113-line `writeup-techniques.md` is the raw card set; this file is the
operational compression — the patterns that repeat across the corpus and the
counter-intuitive ones worth remembering.

---

## 1. The five cards, operationalized

**Card 1 — introspection → named field → flag.** The most common CTF shape.
`{__schema{types{name}}}` returns the type list; a type named `flag`,
`secret`, `super_super_secret_flag_dispenser` is the target. The flag field
may need args (`authorized:true`, `token:"x"`) — the args are the next
problem, not a blocker.

**Card 2 — suggestion oracle when introspection is off.** `did you mean`
errors name real fields. The Intent CTF shape: `_secret{flag}` resolved to
the flag — the underscore-prefixed names are the ones the schema hides.
`map --seed` automates the loop.

**Card 3 — SQLi through an arg.** `getNote(q:"'")` → driver text in
`errors[].message`. The UNION's column count is the resolver's selected
column count — count it from the working query. The sqlite_master /
information_schema dumps land in `data` — the extraction is the same field.

**Card 4 — filter-object backslash escape.** The VolgaCTF shape: two
string fields sanitized per-field but concatenated into one WHERE — a
trailing backslash in the first field escapes its terminator, the second
field becomes raw SQL. Any `filter:{a:..., b:...}` input object is the
candidate.

**Card 5 — unguarded listing feeds guarded field.** `flag(token:)`
demands a token that `users{token}` hands out. The authz is per-resolver —
the listing was never given a check. Grep the schema for the arg name as
a *field name on a different type*.

## 2. The counter-intuitive lessons

- **`__schema` blocked ≠ schema hidden.** `_service{sdl}` survives — it's
  a regular resolver, not introspection.
- **`Cannot query field` ≠ authz.** It means the field *doesn't exist*.
  `Forbidden` means it does.
- **A `null` data field is a real field.** `{"user":null}` ≠ `Cannot query
  field "user"` — the field exists and returned null.
- **The suggestion oracle survives masked errors.** Yoga/Apollo prod mask
  *exception* text but still emit `did you mean` validation hints.
- **The `id` arg type is not an ID.** `"1"`, `1`, `"01"`, `"1e2"`, `"+1"`,
  `" 1"` may all resolve to the same object — canonicalization is the
  ownership-bypass surface.
- **The variables channel bypasses the document parser.** An object in
  `variables` where a scalar was declared skips GraphQL string validation —
  the NoSQLi/prototype-pollution surface.
- **Partial responses are the map.** `data` + `errors` together name exactly
  which fields are authz'd — the nulls are the checked set, the data is the
  open set.

## 3. The framework default matrix

| Framework | Introspection | Suggestion oracle | Batch | GET mutation | Upload |
|---|---|---|---|---|---|
| Apollo ≤3 | on dev, off prod | on | on | spec says no; often yes | via plugin |
| Apollo 4 | on | on | gated | no | via plugin |
| express-graphql | on | on | on | yes (spec violation) | no |
| yoga | on | on | on | yes | yes |
| graphene | on | on | on | yes | via plugin |
| graphql-java | on | no | varies | no | via servlet |
| graphql-ruby | on | no | no | no | via plugin |
| absinthe | on | yes | no | no | yes |
| hotchocolate | on | yes | yes | no | yes |
| juniper | on | no | no | no | no |
| async-graphql | on | yes | yes | no | yes |
| mercurius | on | on | yes | no | yes |
| gqlgen | on | no | yes | no | yes |
| lighthouse | on | on | yes | no | yes |
| postgraphile | on | no | yes | no | no |
| hasura | on | partial | configurable | no | no |

`on` means the default; CTF boxes ship the default.

## 4. The high-yield order

The 80/20 — the five probes that find 80% of GraphQL CTF flags:

```graphql
{__schema{types{name,fields{name}}}}
{_service{sdl}}
{users{email token role}}
{flag(token:"x")}
{node(id:"VXNlcjox"){__typename}}
```

Everything else is depth — these five cover the four cards plus the
federation fallback.

## 5. The negative-result discipline

The corpus's quiet lesson: challenges with "no GraphQL bug" get solved
through GraphQL's *carrier* — the endpoint is the attack surface for
`web-sqli`, `web-idor`, `web-ssti`, `web-ssrf`, `web-file-upload`,
`web-auth-session` — not GraphQL itself. The skill's job is routing the
*bug class* correctly once the carrier is confirmed; the ledger records
the *owning* class.

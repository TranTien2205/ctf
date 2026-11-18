# Detection — finding the identifier and the two-identity proof

IDOR is not a payload class — it is a missing ownership check. Detection
is finding where an identifier addresses a resource, then proving a
second identity can reach it.

---

## 1. What an identifier looks like

Any value that names a specific object:

```
/users/42                    path segment
/user?id=42                  query param
GET /api/orders/1003         REST id
{"user_id":42}               JSON body field
{"order":"inv_2024_0042"}    string id
{"file":"report_42.pdf"}     filename
{"doc":"docs/42.pdf"}        path
{"uuid":"550e8400-..."}      UUID
{"ref":"dGVzdA=="}           encoded
{"gid":"VXNlcjo0Mg=="}       Relay global id (b64 "User:42")
Cookie: user=42              cookie
JWT {"sub":42}               token claim
{"uid":"a1b2c3"}             hex/mongo/sqlite
{"key":"sk_live_42"}         API key naming object
?id=42&id=43                 array of ids
{"ids":[1,2,3]}              bulk array
{"user":{"id":42}}           nested
{"filter":{"owner":42}}      filter field
{"where":{"user_id":42}}     query-builder
{"user_id":42,"role":"admin"} — compound
form field: <input name=uid value=42 hidden>
Referer: /users/42           Referer carries the id
X-User-Id: 42                custom header
X-Forwarded-User: admin      trusted header
```

## 2. The surfaces where identifiers appear

- **REST path**: `/api/users/{id}`, `/api/orders/{id}/items/{item_id}`.
- **Query**: `?id=`, `?user=`, `?doc=`, `?file=`, `?report=`, `?invoice=`.
- **Body**: `{"user_id":}`, `{"account":}`, `{"id":}` on create/update.
- **GraphQL**: `user(id:)`, `node(id:)`, `nodes(ids:)`, a nested object.
- **File**: `?file=report.pdf`, `?download=`, `?path=`, `?doc=`.
- **Header**: `X-User-Id`, `X-Account`, `X-Tenant`, `X-Org`.
- **Cookie**: `user=42`, `account=acme`, `doc=ref`.
- **JWT claim**: `sub`, `uid`, `user_id`, `account`, `tenant`, `org`.
- **Hidden form field**: `<input type=hidden name=account value=42>`.
- **WebSocket message**: `{"type":"get","id":42}`.
- **RPC body**: `{"method":"getUser","params":{"id":42}}`.
- **Batch**: `POST /batch [{"url":"/users/1"},{"url":"/users/2"}]`.
- **Multipart**: a filename field carrying an id.

## 3. The two-identity probe — the only proof

You cannot prove IDOR with one account. The procedure:

```
1. Register account A. Create a resource R (a post, file, order, note).
   Record R's identifier — from the response, the URL, or the object id.
2. Register account B. (Or use no session if the resource needs auth.)
3. As B, request R's identifier via the same route A used.
4. If B reads or writes R → IDOR confirmed.
   If B gets 403/404/empty → ownership enforced → falsifier.
```

The variants that also count:
- B modifies A's object (write IDOR).
- B deletes A's object (delete IDOR — test on YOUR OWN second object first).
- B lists A's objects (collection IDOR).
- B gets A's object via a different format (`/users/42.json` vs `/users/42`).

## 4. What does NOT count

- A `200` with an empty `{}` — no attributable object data.
- A `200` on a *public* object — visibility is not ownership.
- A `200` on A's own object — same identity.
- A `404`/`403` — ownership enforced (or object gone).
- A `302` to login — auth required, not IDOR.
- A guessed id that happens to be public.
- A `200` on a different object than the one requested (misread).

## 5. The ownership marker

To confirm, the response must contain *attributable* data — a field that
proves the object belongs to A, not B:

- A's email/username/id on the object.
- A's private field (a note, a flag, a secret).
- A field only A would set.
- The object's `owner_id`/`user_id`/`created_by` = A's id.

`http_probe --evidence-regex` carries the marker — e.g.
`--evidence-regex '"owner_id"\s*:\s*1|"email"\s*:\s*"a@'` —
the response proves the object is A's.

## 6. The collection-vs-object distinction

- **Object IDOR**: `/users/42` — one object, owned.
- **Collection IDOR**: `/users` or `/orders?user=42` — a list scoped to
  the user; if B can list A's, that's a different check.
- **Field IDOR**: `/users/42` returns A's public fields but B should see
  fewer — the *field* set differs by owner.

## 7. The read-vs-write distinction

- **Read IDOR**: GET another's object — usually safe to test.
- **Write IDOR**: PUT/PATCH another's object — test on your OWN second
  object first; do not corrupt a shared instance.
- **Delete IDOR**: DELETE — test on your own second object only.
- **Action IDOR**: POST to `/orders/42/cancel` — an action on another's
  object.

On a shared instance, *read* another's record; never write it first.

## 8. The "identifier is not the id" edge

The URL says `/users/me` — the id is in the session. Changing the URL
doesn't help; the id is implicit. Look for:
- A `?user_id=` override the handler honours.
- A JWT `sub` claim that names a different user.
- A `X-User-Id` header that overrides the session user.
- A `?account=` that switches the active account.

## 9. The "the id is in the body, not the URL" shape

`POST /api/getData {"id":42}` — the URL is generic; the id is in the
body. Test the body id. Or `POST /api/update {"user_id":43, ...}` —
the update targets a body id.

## 10. The identifier's provenance

Where did you get the id?

- The app handed it to A (response, URL, list) → usable for B's probe.
- You guessed it (`/users/1`) → only proves IDOR if the object is
  attributable AND not public.
- The id is a hash/UUID → it came from somewhere — a leak, a list, a
  predictable generation.

## 11. First-contact sequence

```
1. Login as A. Map the app. Record every identifier that appears
   (path/query/body/response fields).
2. Note the format of each (numeric, UUID, b64, hash, composite).
3. For each identifier, record what resource it addresses and who owns it.
4. Create a test object as A — record its id.
5. Login as B (or use no session).
6. Replay A's identifier through B's session — the two-identity probe.
7. Check the response for A's ownership marker.
```

## 12. The signals that say "look here"

- An id in the URL that increments.
- A numeric id in a JSON body the client can edit.
- A `?file=`/`?doc=`/`?download=` param.
- A GraphQL `node(id:)` or `user(id:)`.
- A JWT `sub`/`uid` claim that names a user.
- A `X-User-Id`/`X-Account`/`X-Tenant` header.
- A `Referer`/`?return=`/`?redirect=` carrying an id.
- An `/api/v1/` vs `/api/v2/` where authz differs.
- A `report`/`export`/`download`/`invoice`/`receipt`/`ticket` endpoint.
- An admin function reachable by URL (`/admin/users`) — function-level.

## 13. The quick oracle

```bash
# As A: create + capture id
curl -s -b a.cookies -X POST "$BASE/api/notes" -d '{"text":"A-private"}'
# response: {"id":1001}

# As B: request A's id
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/notes/1001" --header "Cookie: session=$B_SESSION" \
  --evidence-regex '"text"\s*:\s*"A-private"|"owner_id"\s*:\s*1' \
  --evidence-kind impact --on-match confirms --on-miss refutes
```

A `confirms` means B read A's private note — the ownership check is
missing. The `impact` kind + the `confirms` verdict + the verbatim
response is the proof `hooks.py post-probe` wants.

## 14. The falsifier

Identity B gets `403 Forbidden`, `404 Not Found`, or a `200` containing
only B's own data — the handler scopes the lookup to the authenticated
owner. Record the `refutes` — the route is closed for this class.

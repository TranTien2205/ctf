# Enumeration — mapping the id surface

Before probing, map *every* identifier the app shows you — the URL, the
body, the response, the headers, the token.

---

## 1. The identifier inventory

As identity A, walk the app and record every id:

| Where | Shape | Example |
|---|---|---|
| URL path | `/users/42` `/notes/1001` | numeric, uuid, slug |
| URL query | `?id=42` `?user_id=1` `?doc=42` | numeric, name |
| Body JSON | `{"id":42,"user_id":1}` | numeric, uuid |
| Body form | `id=42&user_id=1` | numeric |
| Response JSON | `{"id":42,"owner_id":1,"user_id":2}` | the object's own + its owner |
| Response header | `Location: /notes/42` `X-User-Id: 1` | id in a header |
| Set-Cookie | `uid=42` `user_id=1` `session_id=abc` | a cookie id |
| JWT claim | `sub:42` `uid:1` `user_id:1` `role:admin` | a claim id |
| GraphQL | `id:"VXNlcjo0Mg=="` `gid://...` `user(id:"...")` | b64 `Type:id` |
| HTML attr | `data-user-id="42"` `data-id="42"` | embedded |
| HTML link | `href="/users/42"` `src="/img/42.png"` | link ids |
| HTML hidden | `<input type=hidden name=user_id value=42>` | hidden field |
| JS source | `fetch('/api/users/'+id)` `user_id:42` | a call's param |
| Filename | `report_42.pdf` `invoice_0042.pdf` | the id in the name |
| Multipart | `filename="doc_42.pdf"` `name="user_id"` | the field/filename |
| Referer | `Referer: /users/42` | the previous id |
| ETag/Last-Mod | `ETag: "42"` | a weak id |
| WebSocket | `{"type":"msg","user_id":42}` | the WS message id |
| SSE | `data: {"id":42}` | the event id |
| Redirect | `302 → /notes/42` | the created object's id |
| Error | `error at /notes/42` `Object 42 not found` | the id in an error |
| Log | `GET /users/42` in an exposed log | the leaked id |

## 2. The response-scrape

The app's own responses carry the ids — scrape them:

```bash
# A's session — list A's objects, record each id
curl -b a.cookies "$BASE/api/notes" | jq '.[] | .id'
# the response's owner/user fields
curl -b a.cookies "$BASE/api/notes/42" | jq '{id, owner_id, user_id}'
# the hidden field
curl -b a.cookies "$BASE/profile" | grep -oE 'data-user-id="[0-9]+"'
# the JWT claim
echo "$JWT" | cut -d. -f2 | base64 -d 2>/dev/null | jq '{sub,uid,user_id,role}'
```

## 3. The "the app hands you the ids" leak

- `GET /api/users` — a user-list leaks every `id`.
- `GET /api/notes?all=true` — a collection leaks its objects' ids.
- `GET /api/search?q=` — a search leaks matching ids.
- `GET /api/autocomplete?q=` — an autocomplete leaks ids.
- `GET /api/feed`/`/api/timeline` — the feed leaks other users' ids.
- `GET /api/leaderboard` — the leaderboard's `user_id`/`rank`.
- `GET /api/comments` — the comments' `author_id`.
- `GET /api/likes`/`/api/reactions` — the reactors' `user_id`.
- `GET /api/followers`/`/api/following` — the user ids.
- `GET /api/team`/`/api/members` — the members' ids.
- `GET /api/share/{token}` — a share's `object_id`/`owner_id`.
- The GraphQL `edges { node { id } }` — every node id.
- A `Location:` on create — the new object's id.
- A `Content-Location:` — the canonical id.
- An `ETag`/`Last-Modified` derived from the id.

## 4. The "the id is in the front-end" leak

- The bundle's hardcoded test ids.
- A `data-*` attribute.
- A comment `<!-- user_id=42 -->`.
- A route `/users/:id` that builds the id from a source the JS controls.
- The sourcemap's original source — `bundle_miner.py` recovers it.

## 5. The "the id is in the error" leak

- `Object 42 not found` — the error names the id.
- `duplicate key id=42` — the constraint error.
- `invalid id 'abc' (expected int)` — the format + the valid ids' shape.
- A stack trace naming `user_id=42`.

## 6. The "the id is in the log" leak

- An exposed `/logs`, `/access.log`, `/debug/requests` — other users'
  ids in the log lines.

## 7. The "the id is in a link" leak

- A `href="/users/42"` on a profile card.
- A `src="/img/avatars/42.png"`.
- A `href="/report/download/42"`.

## 8. The "the id is in the WebSocket" leak

- `{"type":"presence","user_id":42}` — a WS presence event.
- `{"type":"msg","author_id":1}` — a chat message's author.

## 9. The "the id is in the SSE" leak

- `data: {"user_id":42,"event":"join"}` — a server-sent event.

## 10. The "the id is in the Referer" leak

- A `Referer: /users/42` header a request carries.

## 11. The "the id is in the ETag" leak

- `ETag: "42"` / `ETag: "user-42"` / `ETag: "object-42-v3"` — the ETag
  derives from the id.

## 12. The "the id is in the filename" leak

- `report_42.pdf` / `invoice_0042.pdf` / `avatar_1.png` — the id is the
  numeric part.

## 13. The "the id is in the multipart" leak

- `filename="doc_42.pdf"` — the uploaded filename carries the id.
- `name="user_id"` `value="42"` — the form field.

## 14. The inventory output

```
location    | id           | format     | owner | carrier
URL path    | /notes/42    | int        | A's   | path
response    | "owner_id":1 | int        | user1 | body
JWT claim   | sub=42       | int        | A     | token
collection  | /api/users   | leaks ids  | any   | list
graphql     | "VXNlcjo0Mg=="| b64 Type:id| node  | arg
filename    | report_42.pdf| int-prefix | file  | path
```

The inventory names every id, its format, and who owns it — the probe
targets the owned ones.

## 15. The "two-identity" shortlist

From the inventory, shortlist the ids that are *A's* (private, owned)
— those are the probe targets for B. The public/unguarded ones aren't
the proof.

# Failed attempts — what each denial pattern tells you to try next

Every failed probe carries information about WHERE the check lives.
This table maps the observed denial to the layer and the next probe.
The point: a denial is a measurement of the check's position, not just
a miss.

---

## 1. Status-code denial patterns

| Observed | Where the check sits | Next probe |
|---|---|---|
| 403 on foreign id, 200 on own | handler-level owner check — real | different carrier for same id (body-nested), or different verb |
| 404 on foreign id, 200 on own | scoped query (`user.items.find`) | collection endpoint, or nested path `/users/1/items` |
| 404 on ALL ids incl. nonexistent | existence mask — can't split | own-id control + timing to split exists-vs-owned |
| 302 → `/users/me` | id recognized, rewrote to self | the rewrite is the fingerprint — try carrier where no self fallback exists |
| 401/302 → login | authN not authZ | session problem, not IDOR — fix the session first |
| 200 with YOUR data on foreign id | default-to-self fallback | the param is decorative — try every alternate param name |
| 500 on foreign id only | check missing but query crashed | the object exists — error fingerprint; try valid-shape probe |
| 400 "invalid id" on foreign only | id-format check, not ownership | nonexistent same-format id — if also 400, it's format-only |

## 2. The exists-vs-owned split

`404` is ambiguous: "no such object" and "not your object" both return
it. Split with three probes:

```
GET /items/<own>        → 200  (lookup works)
GET /items/<foreign>    → 404
GET /items/<definitely-nonexistent>  → 404
```

Foreign and nonexistent identical → scoped query (object lookup bound
to owner). That's the strongest denial — the check is IN the query.
What still reaches past it:

- **The collection path**: `GET /items`, `?filter`, `?ids[]` —
  collection queries are written separately.
- **The secondary lookup**: `GET /items/<id>/export` — a different
  code path may run `Item.find(id)` unscoped.
- **The mutation path**: PATCH/DELETE — a write check might exist
  while a scoped-read masks the object.
- **Second-order**: the id you can't read may be embeddable in a
  request where the server reads it for you (import, share, clone).

Foreign 404 but nonexistent 500/400 → the foreign object resolved and
something denied it downstream — different fingerprint, a lead.

## 3. "200 but no foreign data" patterns

| Response | Meaning | Next |
|---|---|---|
| `{"data": null}` | resolver-level suppress | field-level vs object-level — probe `id` field only |
| `{"data": {"id": 1, "email": null}}` | partial field authz | the OBJECT resolved — object-level check is missing |
| `{"items": []}` | collection filter kept you out | `?all=true`, `?scope=all`, `?filter=` mutations |
| B's own object returned | silent scoping | param ignored — try nested/dotted names |
| generic wrapper, no fields | serializer hid everything | change Accept/?format — another serializer may leak |
| empty list but `X-Total-Count: N>0` | body filtered, count leaked | the count is your oracle — paginate to position the row |

## 4. Timing-denial patterns

- Foreign-id fetch consistently SLOWER than nonexistent → the row was
  found, then denied. The check is post-lookup; there may be a sibling
  route that returns it.
- Foreign and nonexistent identical timing → scoped query again.
- Nonexistent SLOWER → unusual; possibly a cache-miss path hitting a
  different store — the foreign object might sit in the cache path.

## 5. Shape-denial patterns

| Denied on | Try next |
|---|---|
| path id | query, body-flat, body-nested, header, GraphQL var |
| JSON body | form body, multipart part, JSON-in-form-field |
| `?id=` | `?user_id=` `?id[]=` `?user.id=` duplicate params |
| `{"id":N}` | `{"user":{"id":N}}` `{"data":{...}}` `{"input":{...}}` |
| REST GET | batch endpoint, GraphQL `node()`, export job |
| session auth | API-key path, bearer path, service-token path |
| current version | `?v=1`, `/versions/`, `?rev=`, `Accept: older` |
| active object | `?deleted=`, `/trash`, `/archive`, `/drafts` |

## 6. When everything denies

Consistent denial across all carriers and verbs = the check is at the
model/query layer. The remaining surfaces, in cost order:

1. **A different object type** — `users` checks, `exports`/`reports`/
   `shares`/`notifications` don't.
2. **Second-order** — create an object that references the foreign id
   (comment on it, share it, import it); the server reads it for you.
3. **Mass-assignment** — you can't read their object, but a body field
   may let you bind it (`{"owner_id": you}` on their object via a
   write route).
4. **The minting surface** — any endpoint that returns ids for objects
   you chose (`/share`, `/invite`, `/export`).
5. **Chain card / reclassify** — if none of these exist, the challenge
   probably isn't IDOR at all; `decide.py` will name the next layer.

## 7. Recording the attempt

```
attempt: GET /items/1042 as B (path carrier)
expected: A's marker (email field)
observed: 404 (same as nonexistent-id control)
layer: scoped query — check inside the lookup
next: collection endpoint /items, then export route
recorded: state.py <name> --hypothesis <id> --verdict denied
```

The `layer` line is what makes the attempt valuable — it tells the
next probe (or the next session) exactly where the wall was measured.

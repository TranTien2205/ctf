# Evidence rules — what proves the class

The proof standard: only a *second identity* reaching the *first
identity's* object with *attributable* data.

---

## 1. The ladder

- **surface**: an identifier appeared in the URL/body — a signal, not a
  bug. `inconclusive`.
- **class**: a second identity's request returned *different* data than
  the first's — ownership may not be enforced. `inconclusive` until the
  data is attributable.
- **impact**: identity B read/wrote identity A's object and the response
  carried A's attributable marker (email/id/private field). `confirms`.

## 2. The proof — verbatim

```
Identity A:  GET /api/notes/1001 → {"id":1001,"owner_id":1,"text":"A-secret"}
Identity B:  GET /api/notes/1001 → {"id":1001,"owner_id":1,"text":"A-secret"}
                                                                      ^^ A's data in B's response
```

The marker `"owner_id":1` or `"text":"A-secret"` is the attributable
evidence — `http_probe --evidence-regex '"owner_id"\s*:\s*1|"text"\s*:\s*"A-secret"'`.

## 3. What is NOT proof

- `200 {}` — an empty wrapper.
- `200 {"id":1001}` — an id echo, no object data.
- `200` on A's own object — same identity.
- `200` on a public object — visibility ≠ ownership.
- `404`/`403` — enforced.
- `302` to login — auth required.
- A guessed id that happens to resolve to a public object.
- A `200` where B sees *B's* own objects filtered to A's id (the response
  is empty or B's).

## 4. The write-side proof

```
Identity A:  POST /api/notes → {"id":1002,"owner_id":1,"text":"A-note"}
Identity B:  PATCH /api/notes/1002 {"text":"B-was-here"}
Identity B:  GET /api/notes/1002 → {"id":1002,"owner_id":1,"text":"B-was-here"}
```

B modified A's object — the response carries A's `owner_id` with B's
content. Write-IDOR proven.

**Safety**: test writes on YOUR OWN second object (A's), never on a
third party's. A shared instance may hold other players' data.

## 5. The delete-side proof — read-only first

```
Identity B:  DELETE /api/notes/1003 → 204
Identity A:  GET /api/notes/1003 → 404
```

The object A created is gone under B's delete. Only test delete on A's
own test object.

## 6. The collection-side proof

```
Identity B:  GET /api/orders?user_id=1 → [{"id":1003,"owner_id":1,...}]
```

B listed A's objects via the filter param — the response carries A's
attributable `owner_id`/`email`.

## 7. The field-level proof

```
Identity B:  GET /api/users/1 → {"id":1,"email":"a@...","role":"admin","secret":"flag{...}"}
```

The admin user's row carries `role:admin`/`secret` — the field set
exceeds what B should see.

## 8. The "the response is the proof" rule

`hooks.py post-probe` on `confirms` requires `--response` verbatim and
`--evidence` that's a substring. `http_probe` emits the whole command —
the `--response` is the bytes, the `--evidence` is the ownership marker.

## 9. The "the marker must be attributable" rule

The marker proves the object is A's — not just "an object". A field
that could be B's (`"id":1001`) isn't attributable; a field only A has
(`"owner_id":1`, `"email":"a@t.tld"`, `"text":"A-secret"`) is.

## 10. The falsifier — verbatim

```
Identity B:  GET /api/notes/1001 → 403 {"error":"Forbidden"}
or            GET /api/notes/1001 → 404
or            GET /api/notes/1001 → 200 {"id":1001,"owner_id":2,...B's data...}
```

`403`/`404`/B's-own-data — the lookup is scoped to the session. The
`refutes` verdict records it; the route is closed for read-IDOR.

## 11. The recording

```bash
python3 tools/hooks.py post-probe "$C" --class web-idor \
  --hypothesis-id H1 --verdict confirms --evidence-kind impact \
  --evidence '"owner_id":1,"text":"A-secret"' \
  --response '{"id":1001,"owner_id":1,"text":"A-secret"}'
```

A `confirms` is checked — `--evidence` must be a substring of
`--response`. The two-identity procedure is what makes it `impact`
not `surface`.

## 12. The negative-result record

A `403`/`404`/B's-data is a `refutes` — record it with `--response`
verbatim. The negative closes the route; it is not a licence to sweep
more ids on the same check.

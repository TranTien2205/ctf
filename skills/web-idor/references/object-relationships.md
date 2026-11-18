# Object relationships — IDOR through associations, joins and embeds

The object you can't read directly is often readable through an object
it relates to. Relationship paths are written by different code than
the direct path — the check on `GET /users/1` doesn't automatically
apply to `GET /posts?author_id=1` or `GET /comments/55?include=author`.

---

## 1. The relationship map

For every object type, list its associations — from responses,
front-end calls, or the schema:

```
user ──has many──► posts, comments, orders, sessions, api_keys
post ──belongs──► author(user); ──has many──► comments, tags
order ──belongs──► user; ──has many──► line_items, payments
org ──has many──► members(users), projects, invites
document ──has many──► versions, comments, shares
```

Each edge is a separate authorization boundary. The app checks the
edge it thinks about (usually `user → post` on `GET /posts/:id`) and
forgets the rest.

## 2. Foreign-key filter parameters

Collection endpoints filtering by a foreign key are the leak surface:

```
GET /posts?author_id=1           — all posts by user 1
GET /comments?user_id=1          — all comments by user 1
GET /orders?customer_id=42       — someone's order history
GET /api_keys?user_id=1          — the keys themselves
GET /sessions?user_id=1          — live sessions of another user
GET /notifications?user_id=1     — their notification feed
GET /audit_log?actor_id=1        — their action history
GET /items?owner_id=1&status=all — FK + lifecycle combo
```

The check on `/users/1` says "not your profile" — but
`/orders?customer_id=1` was written as a reporting query and returns
the same user's data through the association.

## 3. Include/embed/expansion parameters

```
GET /posts/9?include=author       — author's full record embedded
GET /posts/9?expand=user,org      — transitive expansion
GET /comments/55?_embed=author    — json-server convention
GET /items/42?fields=*,owner.*    — field-mask traversal
GET /posts/9?populate=author.profile,author.keys
GET /api/items/42?with[]=owner&with[]=org.members
GET /posts/9?join=author          — PostgREST/Supabase style
GET /posts/9?select=*,author(*)   — PostgREST embed syntax
```

The expansion runs inside the serializer — past the handler's check.
`?include=author` returning A's email while `GET /users/1` 403s is
object-leak via relationship. Depth variants:
`?include=author.org.members` chains the leak two edges deep.

## 4. Reverse-relationship leaks

The object you can read references the one you can't — and the
readable one carries a copy:

- `GET /posts/9` → `{"author_id": 1, "author_name": "alice",
  "author_email": "..."}` — denormalized copies leak the fields.
- `GET /orders/42` → `{"user": {...}}` embedded for convenience.
- `GET /comments/55` on your own post → commenter profiles embedded.

Read every object type B legitimately owns or can list; grep the
responses for foreign-user fields. Denormalized copies are invisible
to the direct-check layer.

## 5. GraphQL edges

```graphql
{ post(id: 9) { author { id email keys { token } } } }
{ user(id: 1) { posts { title } orders { total items { sku } } } }
{ node(id: "VXNlcjox") { ...on User { posts { edges { node { title } } } } } }
```

Field-level authz per type is rare; the author edge resolves through
a dataloader with no check. `...on User` fragments on `node()` union
types hit every type the schema exposes. See `graphql-idor.md`.

## 6. The transitive trap — A→B→C leaks

`GET /projects/7` (yours) embeds `members`; a member object embeds
`recent_activity`; the activity embeds `documents` — a document id
you never saw directly. Multi-edge traversal:

```
/projects/7 → members[] → member.activity[] → activity.doc_id
GET /documents/<doc_id> — try it direct now that you hold the id
```

The id hand-off is the point: relationship responses are where
foreign ids come from when the direct space is opaque (uuids, hashes).

## 7. Junction-table objects

Memberships, enrollments, shares, assignments — the join row is itself
an object with its own id:

```
GET /memberships?org_id=7     — the whole member list
GET /enrollments?course_id=9  — every student id
GET /shares?document_id=42    — who else can read it
POST /memberships {"org_id":7,"user_id":<me>} — join their org
```

Junction objects are the most under-checked class — they look
"internal" to developers. `POST /memberships` with a foreign org_id is
the membership-pivot into a tenant (see `multi-tenant.md`).

## 8. Polymorphic associations

`GET /comments?commentable_type=User&commentable_id=1` — polymorphic
FKs let you point the relationship at any type. The check may verify
`commentable` access for one type but not another:

```
?commentable_type=Post&commentable_id=9    → 403 (checked)
?commentable_type=User&commentable_id=1    → 200 (type nobody checked)
?commentable_type=Flag&commentable_id=1    → ?
```

Try every type name in the polymorphic union — schema, error messages,
or source naming reveals them.

## 9. Aggregation endpoints on relationships

```
GET /users/1/stats       /users/1/activity      /users/1/summary
GET /users/1/export      /users/1/report        /users/1/timeline
GET /orgs/7/metrics      /orgs/7/members/count
```

Aggregate endpoints "don't return the object" — they return computed
data over it, and get written without the object's check. A stats
endpoint can leak the flag itself if the flag field is counted,
summed into a response, or shown in a "recent activity" feed.

## 10. Search endpoints as relationship leaks

```
GET /search?q=*&type=user        — the whole table
GET /search?author_id=1          — search scoped by FK
GET /posts/search?user_id=1      — same data, search path
GET /autocomplete?term=a&type=user  — typeahead leaks names/emails
GET /suggest?field=email&prefix=a
```

Search runs a different query builder than the detail endpoint — the
`WHERE` clause carries the FK but not the ownership predicate.

## 11. The probe plan

For each object type T and each association A:

1. `GET /T?fk=<foreign-id>` — collection filter
2. `GET /T/<own-id>?include=A` — expansion of the edge
3. `GET /A-collection?<T-fk>=<foreign>` — reverse edge
4. `GET /T/<own>/<A>` — nested route (`/users/1/orders`)
5. junction object write: `POST /A-join {t_id, foreign}`

Each cell that returns foreign-attributed data is a finding; each
denial is a recorded negative naming the edge that held.

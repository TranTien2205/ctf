# ID supply — where the application hands you foreign identifiers

Opaque ids (uuids, hashes, signed tokens) don't kill IDOR — they move
the enumeration problem to the leak surface. These are the places an
app hands out identifiers for objects that aren't yours. When ids are
unguessable, mine here, not the id space.

---

## 1. In-band surfaces (inside the app)

**Activity feeds and timelines.** "alice created Invoice", "bob shared
Document 550e8400-..." — feed entries embed object ids in links and
payloads. `GET /feed`, `/activity`, `/timeline`, `/recent`.

**Comments and mentions.** A comment object carries `author_id`,
`object_id`, `parent_id`. `@mention` autocomplete leaks user ids with
every keystroke: `GET /users/suggest?q=a` returns `[{"id": "<uuid>",
"name": ...}]`.

**Member/user lists.** `/org/members`, `/team`, `/users`, `/members`,
`/followers`, `/friends` — directories whose per-user rows carry ids.
Search endpoints reach the same rows: `?q=`, `?email=`, `?filter=`.

**Notifications.** `GET /notifications` — "you were added to Project
550e-..." embeds the project id; the notification type enumerates the
object types reachable.

**Shares and invites.** `/shared-with-me`, `/invites`, `/links` —
objects shared TO you still carry owner and object ids. A public share
page (`/s/<token>`) frequently embeds the owner's user id and the
real object id in its JSON bootstrap.

**Search and autocomplete.** `/search?q=*` per type, `/autocomplete`,
`/typeahead`, `/suggest`, `/lookup`, `/resolve`. The response row
includes the id — that is the leak.

**Embeds in owned objects.** Your own objects reference foreign ones:
your comment's `reply_to`, your order's `fulfilled_by`, your message's
`sender_id`, a shared doc's `owner_id`. Read your own rows and extract
the ids they name.

## 2. URL and link surfaces

**Emails.** Registration, share, reset, export-ready emails carry raw
ids and signed URLs: `/verify?uid=42&token=...`,
`/exports/download/<uuid>`. A mailbox you control accumulates every id
the app ever mailed you — including ids minted for other users when
the mail template is wrong.

**Redirects and Location headers.** `POST /items` → `Location:
/items/<uuid>`; `/s/<token>` → `302 /documents/<uuid>` — the redirect
decodes the opaque handle into the real id.

**Canonical/og tags.** Pages for shared objects emit `<link
rel=canonical href="/docs/<uuid>">` and `og:url` with the real id —
the public share page leaks the private object id.

**Print/export URLs.** `/items/42/print`, `/items/42.pdf`,
`/items/42?format=pdf` — a different route template that accepts the
same id, often with a weaker check.

## 3. File and static surfaces

**Uploads and avatars.** `/uploads/<uuid>.png`, `/avatars/<id>.jpg` —
file ids leak record ids when named after them; an avatar URL in a
profile you can't read directly still hands you the id.

**Sitemap/robots.** `sitemap.xml` lists public object urls —
`/posts/<slug-or-id>` for thousands of rows.

**API discovery docs.** `/openapi.json`, `/swagger.json`,
`/api-docs`, `/schema`, `/.well-known/` — examples sections embed real
ids from the dev environment; `graphql introspection` names the id
fields per type.

**Source maps and bundles.** `tools/web/bundle_miner.py` recovers
endpoint templates (`/api/items/${id}`), fixture data, and example ids
from the front-end bundle — `sourcesContent` frequently carries real
dev fixtures.

## 4. Error and debug surfaces

- Stack traces: `Item 550e8400-... not found` confirms a format and
  sometimes leaks a sibling id ("expected one of [...]").
- Validation echoes: `"id 'X' conflicts with existing id 'Y'"`.
- Debug endpoints: `/debug`, `/test`, `/admin/fixtures`,
  `/_profiler`, `__debug_toolbar__`, `/actuator/*`.
- 404 pages that embed the attempted id in context: "No user with id
  550e-... ; did you mean 550f-...?"

## 5. Protocol surfaces

**WebSocket frames.** A live channel broadcasts
`{"event":"created","item":{"id":"<uuid>","owner":"<uuid>"}}` to every
connected client — subscribe and collect the stream.

**GraphQL.** `__schema` names types; any connection field
(`users(first:100){edges{node{id}}}`) is a bulk id source. `node()`
then dereferences each.

**Webhooks/callbacks.** Register a webhook endpoint; event payloads
carry object ids for every event the app emits — including other
users' events when scoping is missing.

**SSE/event streams.** `/events`, `/stream`, `/live` — same broadcast
leak as WebSockets.

## 6. Out-of-band surfaces

- **Public references**: documentation, example screenshots, help
  articles containing real ids.
- **CTF handout artifacts**: README, fixtures, seed data, docker
  compose env, `.sql` dumps, git history.
- **Archive/caches**: Wayback copies of pages with id-bearing urls;
  Google-indexed `/users/<id>` pages.
- **Challenge description**: the narrative sometimes names the target
  id directly ("admin's note") — search the seed for it.

## 7. The composite workflow for opaque ids

```
1. Collect every id the app exposes to B (feeds, comments, embeds)
2. Identify the format (uuid v4 vs v7, hash, b64 — see signed-ids.md)
3. For each collected id, probe the object endpoint as B
4. For each format that is predictable (v1/v7), generate the
   neighbourhood around a collected id
5. For each type named in the schema, try Type:1 / small ints in the
   format's encoding
```

The ids the app leaks are worth more than the ids you guess — every
collected foreign id is a confirmed-existence object with a known
owner context.

## 8. Recording

```
id-source: GET /api/notifications as B
ids-collected: 4 (2 users, 1 project, 1 doc)
format: uuid v7 (time-ordered)
next: probe /api/projects/<uuid> and /docs/<uuid> direct;
      generate v7 neighbourhood for the doc id
```

Log where each id came from — the leak surface itself is often the
report (e.g., notifications leaking every tenant's project ids is
already a finding).

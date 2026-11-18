# Lifecycle IDOR — where the check diverges across the object lifecycle

Objects move through states: created → active → updated → shared →
archived → deleted. Authorization checks are usually written for one
state and rot in the others. Map the lifecycle; the bug lives in the
transition nobody wrote a check for.

---

## 1. The state graph

```
            ┌──────────┐   update    ┌──────────┐   archive   ┌──────────┐
 create ──► │  active  │ ──────────► │ updated  │ ──────────► │ archived │
            └────┬─────┘             └──────────┘             └────┬─────┘
                 │ share/publish                                   │ restore
                 ▼                                                 ▼
            ┌──────────┐   delete    ┌──────────┐             ┌──────────┐
            │  shared  │ ──────────► │ deleted  │ ◄────────── │ restored │
            └──────────┘             └──────────┘             └──────────┘
```

The check typically exists for `active` reads. The gaps:

## 2. Deleted-but-readable

`DELETE` marks `deleted=true` instead of removing the row. Probes:

- `GET /api/items/<deleted-id>` — does the read path filter
  `deleted=false`? If not, deleted objects read fine, including other
  users' deleted objects whose ids you already hold.
- `GET /api/items?include_deleted=true` / `?deleted=true` /
  `?with_trashed=1` / `?state=any` — filter parameters that widen the
  scope. Rails/paranoia-style soft-delete often honours
  `?with_deleted`, Laravel `?withTrashed`, Django a custom param.
- `GET /api/trash` `/api/deleted` `/api/archive` — a separate endpoint
  serving tombstoned rows, frequently missing the ownership scope the
  main endpoint had.

## 3. Draft and unpublished states

Drafts (`status=draft`, `published=false`) are private by intent. The
collection endpoint may list `published=true` only, while the object
endpoint reads any status — a foreign draft id from a leak (share
link, search index, `?status=all`) reads despite never being
published. Probe matrix:

```
GET /items?status=draft      — can B list A's drafts at all
GET /items/<draft-id>        — can B read A's draft directly
GET /items/<draft-id>/preview — the "preview" route often skips checks
GET /preview?token=...       — signed-preview vs plain-id preview
```

## 4. Shared / published objects

Sharing mints a public link: `/shared/<token>` or
`/items/<id>?share=abc`. Gaps:

- The share token is the object id itself (`/shared/42`) — sequential
  shares enumerate the world.
- `?share=` with any non-empty value flips the object into a
  public-read path even when the token is wrong — `?share=x` vs absent
  is the discriminating probe.
- Sharing grants `shared_with: [user B]` — the check tests membership
  but not the permission (`viewer` vs `editor`), so a viewer writes.
- Unshare leaves a stale token valid (token never invalidated).

## 5. Versioned objects

`/items/42/versions/3`, `?v=3`, `X-Version: 3` — a versioned object
stores history. The check on the current object may not apply to
historical versions: `GET /items/42/versions` lists A's edit history
including deleted field values (the flag set then removed — a classic
CTF shape). Also `/items/42?rev=1`, `/items/42/diff?from=1&to=2`.

## 6. The create-then-read chain

When you cannot guess foreign ids, make the app hand you one:

1. `POST /items` as A → response carries `id: 1042` and often a
   `owner_id` or slug.
2. As B, that id is now a known foreign id — the enumeration problem
   is solved by A's own create.
3. Other minting surfaces: search results, comments naming the object,
   activity feeds (`user 1041 created item 1042`), notification
   payloads, email links, invitation urls, sitemap.xml.

## 7. Ownership-transfer endpoints

`POST /items/42/transfer {"new_owner": <me>}`, `.../assign`,
`.../claim`, `.../accept` — the transfer verb is a write-shaped IDOR
that flips ownership rather than just reading across it. Signals:
`transfer`, `assign`, `claim`, `handoff`, `give`, `move_to`,
`change_owner`, `reassign`. Probe with A's object id and B's user id;
a missing owner-check on transfer is full account takeover of the
object — read it after claiming.

## 8. Archival and export states

Exports (`/items/42/export`, `/export?format=pdf&ids[]=42`,
`/reports/generate`) run through a different code path than reads —
frequently a background job that re-fetches by id *without* the
request context's ownership check:

1. `POST /exports {"ids":[42]}` — queue an export of a foreign id.
2. `GET /exports/<job-id>` — the job result contains the foreign row,
   even though `GET /items/42` denied.

The async-report shape is the most reliable lifecycle gap: the
authorization lives on the API path, and the worker path trusts the
queued ids.

## 9. Restore / undelete / clone

`POST /items/42/restore`, `POST /items/42/clone`, `POST /items/42/
duplicate` — state-change verbs distinct from read/update. A clone of
a foreign object returns a *new* object you own containing the foreign
data — the read happens server-side where no check runs. Clone is the
highest-value lifecycle verb to probe.

## 10. Probe matrix per lifecycle

| Verb | Route shape | The gap |
|---|---|---|
| read deleted | `GET /items/<del-id>` | no `deleted=false` filter |
| list deleted | `?include_deleted=1` | param widens scope |
| read draft | `GET /items/<draft>` | status filter only on list |
| preview | `/preview/<id>` | preview route unscoped |
| versions | `/items/42/versions/1` | history unscoped |
| transfer | `POST /items/42/transfer` | ownership check missing |
| export | `POST /exports {ids:[42]}` | worker path unscoped |
| clone | `POST /items/42/clone` | copy without check |
| restore | `POST /items/42/restore` | tombstone readable |
| share | `?share=x` | any token flips public path |

Run the matrix once per object type with B's session against A's ids.
Each cell that returns foreign data is a finding; each denied cell is
a recorded negative that closes that lifecycle path.

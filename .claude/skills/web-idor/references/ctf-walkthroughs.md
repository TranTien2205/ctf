# CTF walkthroughs — IDOR shapes as they actually appear

Annotated probe-by-probe traces of the five IDOR challenge shapes that
recur in jeopardy events. Each names the observation, the hypothesis,
the discriminating probe, and where the flag was hiding.

---

## Shape 1 — "the profile endpoint"

**Observation.** `GET /api/user/1042` returns the logged-in user's
profile. Numeric id in the path; session cookie auth.

**Hypothesis.** Object-level check missing; neighbouring ints are other
users.

**Probe.** Register two accounts (A gets id 1041, B gets 1042). As B:
`GET /api/user/1041` → A's email/username in the body. Control:
`GET /api/user/99999` → 404 (distinguishes real lookup from
default-to-self).

**Where the flag was.** User id `1` (admin) — `GET /api/user/1` as B
returned `{"id":1,"name":"admin","flag":"..."}`. The admin object
carried the flag as a field. Adjacent-id probing found nothing; the
payoff was the known-small id.

**Lesson.** Sweep small ints (0–10) before adjacency — CTF flags live
in object id 1, the admin, the first user, the first note. Adjacency
proves the bug; small ints find the flag.

## Shape 2 — "the invoice/download"

**Observation.** After ordering, `GET /download/invoice_1042.pdf`.
Filename carries the record number.

**Hypothesis.** Path object-id with no ownership check on the static
handler.

**Probe.** `GET /download/invoice_0001.pdf` → 200, a PDF with another
user's name and `flag{...}` in the text layer (extract with
`tools/web/pdf_text.py`). Traversal sibling: `GET
/download/invoice_1042.pdf/../flag.txt` — usually dead on modern
static servers, but worth one probe since the filename pattern
advertises path handling.

**Lesson.** File-IDOR objects are frequently PDF/text exports — the
flag hides in the document body, so extract, don't just status-check.
Zero-padded ids (`invoice_0001`) mean the pad width matters; match
the observed format exactly.

## Shape 3 — "the GraphQL node"

**Observation.** Front-end calls `{node(id:"VXNlcjo0Mg=="){...on
User{name}}}` — Relay global ids.

**Hypothesis.** `node()` resolves any type by id; the per-type check
exists on `user(id:)` but not on `node(id:)`.

**Probe.** Decode → `User:42`. Re-encode `User:1` → `VXNlcjox`. Query
`{node(id:"VXNlcjox"){...on User{name,email}}}`. Also try other type
prefixes from the schema: `Flag:1`, `Note:1`, `Admin:1`.

**Where the flag was.** `node(id:"RmxhZzox")` (`Flag:1`) — the Flag
type had no authorization at all because the app assumed it was only
reachable through a checked parent.

**Lesson.** `node(id:)` bypasses per-field resolvers; enumerate type
names from introspection (`__schema { types { name } }`) and try the
interesting ones as `Type:1`. See `graphql-idor.md`.

## Shape 4 — "the update that binds"

**Observation.** `PATCH /api/profile {"name":"..."}` — a profile
update. GET reads fine, id is implicit from session.

**Hypothesis.** The binder maps extra body keys onto the user row —
mass-assignment to a foreign `id` or a privilege field.

**Probe.** `PATCH /api/profile {"name":"x","id":1}` → then
`GET /api/profile` → profile of user 1 (the session now resolves
another row), or `{"is_admin":true}` then check an admin route.

**Where the flag was.** Setting `"id":1` rebound the session's user;
`/api/profile` then returned the admin row with the flag. A variant:
`{"role":"admin"}` unlocked `/admin/flag`.

**Lesson.** Write endpoints that bind the whole body are the
mass-assignment surface. Corpus: `id`, `user_id`, `role`, `is_admin`,
`admin`, `isAdmin`, `tenant_id`, `verified`, `permissions[]`. One
field per probe; a 200 with no effect means the key was dropped —
the next key, not a variant.

## Shape 5 — "the receipt that isn't yours"

**Observation.** Order confirmation page calls `GET
/api/orders/7f3a.../receipt` — a uuid, so "not enumerable".

**Hypothesis.** Either (a) uuid is time-ordered (v1/v7 → neighbours
predictable), or (b) uuid is random but the order list endpoint leaks
other ids.

**Probe.** Identify the version digit (`7f3a**1**...` = v1). If v1/v7:
extract timestamp, generate the uuid range for the ordering window
(see `uuid-analysis.md`). Regardless: check `GET /api/orders` (list),
`GET /api/orders?limit=100`, `GET /api/admin/orders` — collection
endpoints frequently return every user's rows.

**Where the flag was.** `GET /api/orders?status=all` returned every
tenant's orders; one row's `note` field carried the flag. The single-
object check was real; the collection filter parameter was the bug.

**Lesson.** Random ids don't kill IDOR — they move it to the
collection endpoint, the search endpoint, or the id-leak surface
(an order page embedding `ordered_by: <uuid>`). When ids are opaque,
hunt where the app hands them out, not how to guess them.

## The pattern across all five

1. The check is almost never *absent* — it is on the wrong carrier
   (path vs body), wrong layer (field vs object), or wrong endpoint
   (single vs collection).
2. The flag lives in a known-small id (`1`), a known type (`Flag`),
   or a known marker field (`note`, `flag`) — enumerate the
   interesting set, not the world.
3. The proof is always the same: B's session returns a field only A
   could own, with B's own fetch as the control.

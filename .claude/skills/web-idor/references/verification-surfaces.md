# Verification surfaces — where ownership evidence actually appears

A 200 is not an IDOR finding. Ownership proof lives in specific
response surfaces, and each surface has a different evidentiary
weight. This module names where to look and what counts.

---

## 1. The ownership-marker contract

For identity A's object, pick markers BEFORE sending B's probe:

- a field only A could set (A's email, A's private note text, A's
  filename),
- a foreign `owner_id`/`user_id`/`tenant_id` value,
- a timestamp/`created_by` that differs from B's own objects,
- content length/class difference vs B's own fetch of its own object.

The probe's job is to put A's marker in B's response. Anything less is
a candidate, not a confirm.

## 2. Body surfaces, ranked

| Surface | Weight | Why |
|---|---|---|
| A's private field in B's 200 JSON | proof | the object crossed the boundary |
| A's `owner_id` ≠ B's id in the record | strong | shows whose object it is |
| a list containing A's row under B's query | strong | collection-level leak |
| 200 with generic/empty wrapper | weak | the check may silently scope to B |
| 200 with B's own fields only | negative | the check rewrote the id to B's |
| 404 for every foreign id | ambiguous | object-existence vs ownership check — probe a nonexistent id to split them |
| 401/403/redirect to login | negative-ish | check exists; test whether it is authN or authZ |
| 500/400 on foreign id only | lead | the object exists; the error is a fingerprint |

The 200-with-B's-own-data case matters: many handlers on a bad id
fall back to the caller's object. `GET /users/9999` returning B's
profile means the lookup defaulted — not an IDOR, and not a denial;
the carrier never reached a check at all.

## 3. Header and metadata surfaces

- `Location` on a 3xx: `/users/42 → 302 Location: /users/me` means the
  handler recognized the id as foreign and redirected to self. The
  object exists; the check rewrote rather than denied.
- `ETag`/`Last-Modified` differences per id — an existence oracle when
  bodies are normalized.
- `X-Total-Count`, `Content-Range`, `Link` headers on collections —
  counts that include foreign rows.
- `Set-Cookie` issuing a context for the foreign object (a
  `viewing_tenant=7` cookie minted by fetching tenant 7's object).

## 4. Timing and side-channel surfaces

When bodies are identical:

- **Timing**: fetching an existing foreign object (query hits a row)
  vs nonexistent (miss) usually differs by milliseconds — measurable
  over ~20 samples. Existence ≠ read access, but it proves the object
  is reachable past the auth layer.
- **Error-channel deltas**: `500` vs `404` vs `403` as an
  existence/existence+denied/existence+allowed triad.
- **Secondary writes**: fetching foreign id logs an activity row,
  bumps a view counter, or fires a webhook — check your own object's
  view count after B fetches it. A changed counter proves the handler
  executed against A's object.
- **Email/notification surfaces**: requesting `GET /users/1` triggers
  "someone viewed your profile" to user 1 — the notification proves
  the lookup ran, even if the response hid the data.

## 5. Write-verb surfaces

For PATCH/PUT/DELETE the evidence surfaces differ:

- **Reflected echo**: `PATCH /users/1 {"name":"x"}` → `{"id":1,
  "name":"x"}` — the echo carries the foreign id; read back as A to
  confirm the write landed (`GET` as A shows the new name).
- **Diff via A's session**: the cleanest proof — B writes, A reads the
  change. On shared instances use a reversible no-op write (same
  value) rather than a real change.
- **Conditional headers**: `If-Match`/`ETag` mismatches reveal
  existence: `412` for existing foreign objects, `404` for
  nonexistent.

Never make the first write probe destructive. Set the field to its
current value (a no-op that still exercises the check), or to a value
you can restore.

## 6. GraphQL surfaces

```json
{"data":{"user":null},"errors":[{"message":"Forbidden","path":["user"]}]}
```

Three surfaces inside one response: `data` (null vs object),
`errors[].message` ("Forbidden" vs "Not found"), and `errors[].path`.
A resolver that returns `null` silently is indistinguishable from
"no such object" — probe an id you know exists (yours) through the
same resolver to get the true-null baseline.

Partial-leak shape: `{"data":{"user":{"id":"42","email":null}},
"errors":[{"message":"Forbidden","path":["user","email"]}]}` — the
object resolved (IDOR on the node) while a field-level check held.
That is a real finding: the object-level check is missing even though
the field-level one fired.

## 7. The "public object" trap

A 200 carrying A's object is not a finding if the object is public —
shared, published, or world-readable by design. Split it:

1. Fetch the id unauthenticated. 200 → public object, not IDOR.
2. Fetch as B a *private* object of A's (one A explicitly marked
   private, or a type that is never public: password reset token,
   draft, invoice, session record).
3. Only the private-type fetch crossing the boundary counts.

Record the object's visibility state with the probe — "A's draft,
visibility=private, read by B" is the claim; "A's profile, public"
is not a claim.

## 8. Negative-result recording

Each denied probe needs four fields for the ledger:

```
carrier: path | query | body-flat | body-nested | header | gql-var
probe: GET /users/1 as B
expected: A's marker field in body
observed: 200 {"id":1,"name":"<B's own name>"}   ← default-to-self
verdict: denied (handler rewrote id to session owner)
next: try body-nested carrier, or different object type
```

"Denied" with the observed reason is worth a dozen unlogged probes —
`decide.py` counts recorded negatives toward the budget and uses them
to pick the next layer.

## 9. The double-fetch control

Every confirmation needs its control fetch: B requests `id=A's` AND
`id=B's` in the same session. The pair proves the marker came from
A's object, not from a handler that always returns the caller's data.
No control → candidate only. This is the single most-skipped step and
the reason most "IDOR found" claims collapse under review.

# Common mistakes — the IDOR anti-patterns

The failure modes that waste probes.

---

## 1. One-account "proof"

Claiming IDOR from one account — the object you read was yours. Two
identities are the only proof.

## 2. The `200 {}` false positive

`GET /users/1` → `200 {}` — an empty wrapper, not object data. The
response must carry attributable data.

## 3. The public-object false positive

`GET /posts/1` → `200` — the post was *public*. Visibility is not
ownership — check whether it's actually private to A.

## 4. The same-object misread

`GET /users/me` → `200` — that's your own object. `me`/`self`/`current`
resolves via session — it isn't an id you addressed.

## 5. The `404` = "guarded" confusion

`404` can mean "not yours" (hidden) or "doesn't exist". A `404` isn't
proof of ownership enforcement — it's ambiguous. The differential
(`403` on id=1, `404` on id=9999) is the existence oracle.

## 6. The `302` = "guarded" confusion

`302 → /login` means unauthenticated — not "the object is guarded".
With a session it may return 200.

## 7. Sweeping before checking

`id_sweep` over 1-1000 before testing the two-identity probe — the
sweep finds ids but doesn't prove ownership. Two identities first.

## 8. Testing write before read

`DELETE /users/1` on a shared instance — you deleted someone else's
object. Read another's, write your own second object.

## 9. The "the format is the id" miss

`id=VXNlcjo0Mg==` — it's b64 `User:42`. You swept `id=1,2,3` while the
real id was `User:1` encoded. Decode before assuming the format.

## 10. The "the carrier is the body" miss

`POST /api/data {"id":42}` — you tried `?id=42` while the real carrier
was a body field. Map every carrier.

## 11. The "the check is on a different field" miss

The check is `object.owner_id == session.user_id` but you probed
`?user_id=` — the override is a *different* field (`?owner_id=`).

## 12. The "the check is on the parent" miss

`/users/1/orders/42` — you checked the `42` but the check is on the
parent `1` (which matches your session). The child lookup may skip the
parent check.

## 13. The "the boundary is the flag" miss

`GET /users/1` returns admin's row but the flag field is missing — the
flag isn't on the object; it's on `/admin/flag` or the file the id
leads to. The IDOR is the reach, not the flag.

## 14. The "the token IS the session" assumption

You forged the JWT `sub` but the session is server-side — the JWT is a
key into the store; claims only bind if verified. See `web-auth-session`.

## 15. The "the leak is the id" assumption

You found `id=42` in a log — but it's a public object's id. A leaked
id isn't a private one — the leak must name an *owned* object.

## 16. The "the guess is the id" trap

You guessed `id=1` — a `200` proves nothing (it could be public/default).
Only an id the app *handed* to A (or a recomputable predictable one)
proves IDOR.

## 17. The "the response proves it" surface-read

`{"id":42,"role":"user"}` — that's *your* object re-echoed, not A's.
The `role`/`owner` field must be *A's* value, not the default.

## 18. The "the id is reachable = vulnerable" gap

`/users/42` reachable by B is only IDOR if `42` is A's *private* object.
A public user profile reachable by all isn't IDOR.

## 19. The "one method" closure

`GET /users/1` → 403 → "guarded". But `PUT`/`PATCH`/`DELETE`/`POST`/
`HEAD`/`OPTIONS`/the `.json` variant may differ. One method's `403` is
not the class's falsifier.

## 20. The "one carrier" closure

`?id=1` → 403 → "guarded". The body/header/cookie/GraphQL carrier may
not be checked. One carrier's `403` isn't the falsifier.

## 21. The "the ORM protects" assumption

`Model.find(42)` — the ORM doesn't scope by owner by default; the
developer must add `find_by(id:, user:)`. "It's an ORM" isn't a check.

## 22. The "the framework protects" assumption

Rails/Laravel/Django have authorization *patterns*, not defaults — the
developer adds `before_action`/`@login_required`/`authorize()`. The
framework doesn't auto-scope.

## 23. The "the id is too long to sweep" excuse

A 128-bit id can't be swept — but it can be *leaked* (a list endpoint,
a referer, a GraphQL dump) or *predicted* (uuid v1, ObjectId timestamp,
hash-of-name). The attack surface is the leak/predict, not the sweep.

## 24. The "the authz middleware covers all" assumption

`app.use(auth)` mounted *after* routes — the later routes are
unprotected. The middleware order is the bug.

## 25. The "the failed-write is negative" misread

`PUT /objects/42` → `400` — validation failed, not ownership. `400`
says the body was wrong; `403`/`404` says the ownership. Distinguish.

## 26. The "the confirm came from the format" misread

`.json` vs `.html` returning different data isn't IDOR — it's a format
handler. The ownership marker must be *A's* data, not the format's.

## 27. The "the second-order is proven" assumption

A stored XSS that *would* reach an admin — you haven't proven the admin
visits. The second-order needs the actual second hop.

## 28. The "the writeup is the recipe" trap

The writeup's id was sequential; yours is a UUID. The class matches;
the probe must re-derive.

## 29. The ledger-less re-walk

Re-running `id_sweep` over a range already closed. The ledger is the
memory — `decide.py` skips it.

## 30. The "every endpoint is checked" assumption

`/api/v1/users/1` guarded, `/api/v2/users/1` not — one route's check
isn't the class's. The version/route variant is the bug.

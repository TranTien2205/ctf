# Authenticated bundle — mining behind the login

## The gated-bundle case

Some apps serve the bundle only to logged-in users — the entry page is
a login wall; the SPA loads after auth. The authenticated bundle is a
*richer* surface: the routes, endpoints, and config a guest cannot see.

## The fetch with session

```bash
# pass the session to bundle_miner
python3 tools/web/bundle_miner.py --url "$BASE/app" \
  -H "Cookie: session=$SESSION" --out recovered/
# or fetch the bundle directly
curl -s -H "Cookie: session=$SESSION" "$BASE/static/js/app.js" -o app.js
curl -s -H "Cookie: session=$SESSION" "$BASE/static/js/app.js.map" -o app.js.map
```

## What the authenticated bundle adds

| Guest bundle | Authenticated bundle adds |
|---|---|
| the login shell | the full route table (admin, internal, user) |
| public endpoints | the user/admin API surface |
| public config | the per-user config, flags, feature gates |
| no secrets | possibly user-scoped keys, a token format |

## The per-role bundle

An app may ship *different* chunks per role — a `user` bundle and an
`admin` bundle, or a lazy admin chunk loaded only for admins. Fetch the
bundle as each role; the admin bundle's route table is the gated surface.

```bash
# as admin
curl -s -H "Cookie: session=$ADMIN" "$BASE/static/js/app.js" -o app_admin.js
# diff the routes the admin bundle names vs the user bundle
```

## The lazy-role chunk

Even on one bundle, the admin module lazy-loads on a role check —
`import('./admin')` behind `if (user.role==='admin')`. The chunk is
public; the *load* is gated. Fetch the lazy chunk directly — the file
is served regardless of role.

## The route-guard lesson

`meta.requiresAuth`, `canActivate`, `beforeEach` guard — a *client-side*
guard on a route whose code + endpoints are still shipped. The guard
hides the page, not the file; the endpoint it calls is the target.

## The session-token format

The authenticated bundle reveals the token format — JWT claims, a
custom session scheme, where the token is stored/sent — a lead for
`web-auth-session` (forge/manipulate the session).

## The verify-with-session rule

An endpoint that 401s as a guest may 200 with the session — verify the
bundle's endpoint leads *with* the session, not just unauthenticated.
A gated endpoint is still a real target.

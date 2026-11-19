# Route guard — the client-side protection that ships the code anyway

## The guard surface

The client guards routes with checks it runs itself — `meta.requiresAuth`,
`beforeEach`, `canActivate`, `RequireAuth`, `PrivateRoute`, a role check
in render. The guard hides the *page*; the code and its endpoints are
still shipped.

## The guard patterns

```bash
# react-router guards
grep -oE '(Private|Protected|RequireAuth|Auth)(Route|Guard|Boundary)' bundle.js
grep -oE 'meta\s*:\s*\{[^}]*requiresAuth[^}]*\}' bundle.js
# vue-router beforeEach
grep -oE 'beforeEach\s*\([^)]*requiresAuth[^)]*\)' bundle.js
# angular canActivate/canLoad
grep -oE 'can(Activate|Load|Deactivate)\s*:\s*\[?[^\]]*\]' bundle.js
# a render-time role check
grep -oE '(isAdmin|role\s*===?\s*["'"'"']admin|user\.admin|checkRole)' bundle.js
```

## The guard-is-client-side rule

A `requiresAuth`/`canActivate`/`PrivateRoute` is a *client-side* check —
the gated component, its lazy chunk, and the endpoints it calls are all
served regardless. The guard only hides the route in the UI; it does
not remove the code or block the endpoint.

## The gated-component lead

```js
<PrivateRoute path="/admin" component={AdminPanel} />
```

`AdminPanel` is shipped (or lazy-loaded) — its code carries the admin
endpoints. The guard says "this is protected"; the file says "here is
how it works". Mine the gated component for the endpoints the UI never
shows.

## The server-side check

The critical falsifier: does the *server* enforce the gate? A
client-side `PrivateRoute` is bypassable by calling the endpoint
directly; a server-side role check is not. Probe the gated endpoint — a
`403` that stays `403` even with a session means the server enforces it.

## The role-flag lead

`isAdmin`, `user.role`, `user.admin` — a client-side privilege flag the
client reads to gate the UI. If the server trusts a client-sent `role`
or `is_admin` param, it is a `web-mass-assignment`/`web-logic-flaw`
lead — the client showed which flag it checks.

## Route

| Guard finding | Route |
|---|---|
| a gated endpoint that is public | `web-idor`/`web-logic-flaw` |
| a client `role`/`isAdmin` the server reads | `web-mass-assignment` |
| a lazy admin chunk | mine it for admin endpoints |
| a server-side gate | dead lead — record |

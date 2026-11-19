# Attack shapes (deep) — the exploit paths the map opens

## Shape: hidden endpoint → its class

The map names `/api/admin`, `/internal/export`, `/v2/debug` — endpoints
the UI gates but the server may not. Each verifies to a real target and
routes to its class. The map is the discovery; the exploit is the
endpoint's own class.

**Variant — param endpoint**: `/api/x/{id}` → `web-idor`; `?q=` →
`web-sqli`; `?url=` → `web-ssrf`; `?file=` → `file-read`.

**Variant — verb endpoint**: `/admin/export`, `/internal/dump`,
`/debug/exec` — a server verb; route to `web-logic-flaw`/its class.

## Shape: leaked credential → authenticated reach

`apiKey`, `token`, `secret`, a JWT, a private key — a real credential
in client source. Verify it authenticates; use it to reach the gated
surface. Route to `web-auth-session`.

**Variant — a session-format lead**: the bundle reveals the token
format (JWT claims, a custom scheme) — a `web-auth-session` forge/
manipulate lead.

## Shape: feature flag → gated behavior

`feature.X`, `config.debug`, `flags.internal`, `meta.requiresAuth` —
the client checks the flag, the server trusts the request. Setting the
flag reaches the gated code path. Route to `web-logic-flaw`/
`web-mass-assignment`.

**Variant — a `role`/`is_admin` param**: the client reads `user.role`
to gate; if the server trusts a client-sent `role`, it is a
mass-assignment privilege change.

## Shape: internal URL → SSRF reach

`http://internal.svc`, `api.internal.*`, a webhook URL, a `postgres://`
string — a host the client calls but the browser cannot reach. An SSRF
surface reaches it. Route to `web-ssrf`.

## Shape: source → sink → its class

A recovered `sourcesContent` shows the real logic — `eval`, `innerHTML`,
`deserialize`, `exec`, a `fetch` — the sink the challenge wants. The
map recovered the spec; the source shows the vuln. Route to the sink's
class.

## Shape: flag in source → gated flag

A `const FLAG`, a `// flag{` comment, an env-inlined flag — the flag
itself in client source. `pre-flag` it, prove it against a
live/artifact response.

## Shape: map → adjacent disclosure → server source

The `.map` is the lax signal → `.git`, `.env`, backups, `src/` are
likely shipped. `.git` recovers the server source — the bigger leak.
Route to `web-info-disclosure`/`file-read-primitives`.

## Shape: route guard → public gated endpoint

`PrivateRoute`/`requiresAuth`/`canActivate` gates a route whose code +
endpoints are shipped. The guard is client-side; the endpoint is
public. Route to `web-idor`/`web-logic-flaw`.

## The chaining note

The map is rarely the whole exploit — it is the discovery layer that
names the endpoint, key, flag, or sink. The chain is: mine → lead →
verify → route → exploit. The map's value is replacing brute force with
the client's own route table.

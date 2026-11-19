# Attack shapes — how the map feeds the exploit

## Shape: hidden endpoint → IDOR/logic

The map names `/api/admin/users`, `/internal/export`, `/api/v2/debug` —
endpoints the UI gates but the server may not. The map is the
*discovery*; the exploit is the endpoint's own class. Route each to
`web-idor`/`web-logic-flaw`.

## Shape: leaked key → authenticated reach

`apiKey`, `token`, `secret`, a JWT — the client source carries a real
credential. Verify it live (it authenticates), then use it to reach the
gated surface. Route to `web-auth-session`.

## Shape: feature flag → gated behavior

`feature.X`, `config.debug`, `flags.internal` — the client checks the
flag, the server trusts the request. The map names the flag and its
endpoint; setting it reaches the gated code path. Route to
`web-logic-flaw`/`web-mass-assignment`.

## Shape: internal URL → SSRF reach

`http://internal.svc`, `api.internal.example.com`, a webhook URL — a
host the client calls but the browser cannot reach directly. An SSRF
surface reaches it. Route to `web-ssrf`.

## Shape: source → sink

A recovered `sourcesContent` file shows the real logic — a template
render, a deserialization, an eval, an unsafe fetch — the sink the
challenge wants. The map recovered the spec; the source shows the vuln.
Route to the sink's class.

## Shape: flag in source → gated flag

A `const FLAG`, a comment, an env value — the flag itself in client
source. `pre-flag` it, prove it against a live/artifact response.

## The chaining note

The map is rarely the whole exploit — it is the *discovery* layer that
names the endpoint, key, flag, or sink the exploit then attacks. The
chain is: mine → lead → verify → route → exploit. The map's value is
replacing brute force with the client's own route table.

## Shape: client-route → server-endpoint confusion

A react-router path `/admin` is client-side — but some map to server
endpoints `/api/admin`. Test each named route against the API prefix;
the ones that respond are real, the 404s are client-only.

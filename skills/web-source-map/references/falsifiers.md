# Falsifiers — what disproves each step

## "There's a bundle here"

Falsifier: the entry page loads no `.js` bundle — a server-rendered app
with no SPA, or scripts that are only a CDN library. The recon surface
is the front-end *application* logic; a page with no app code is not
this route.

## "The map is reachable"

Falsifier: `<bundle>.js.map` returns 404, or returns 200 with
`text/html` (a catch-all route serving the index page, not a map). A
real map is `application/json` starting `{"version":3`. Status alone
does not confirm — the content type and first bytes do.

## "The map has source"

Falsifier: the map exists but `sourcesContent` is null/absent — you get
the file names, not the text. That is a partial: the structure, not the
source. Do not claim "recovered the source" when you recovered the file
list.

## "The bundle holds secrets"

Falsifier: every high-entropy string is a minified identifier, a hash,
or a class name — `bundle_miner`'s secret candidates all fail the live
check, or the `--context` shows them in dead/non-secret positions. A
secret-shaped string that never verifies is not a finding.

## "The endpoint is real"

Falsifier: a string `/api/admin` in the bundle 404s live — the route
was a dead code path, a renamed endpoint, or a client-side route not a
server one. A string in the bundle is a *claim* the client makes;
verify the endpoint responds before treating it as real.

## "This is a vulnerability"

Falsifier — the deepest one: the map gave endpoints and secrets, but
none of them are exploitable — the endpoint is public-by-design, the
key is a publishable client key (`pk_live_`), the admin route is
server-side-gated. The map is *recon*; it produces leads, not bugs.
The finding is the follow-on class the map fed.

## The honest dead end

A mined bundle that produced only public endpoints and publishable keys
is a clean negative — record it: "bundle mined, N endpoints all public,
no real secret, map absent". The next solver does not re-mine the same
bundle hoping the strings changed.

## The map-traversal note

A `sources` path that escapes `--out` (a `../../..` traversal) is a
signal the map is hostile, not a successful recovery — `bundle_miner`
rejects and counts it. A map whose sources all traverse is not a clean
recovery; treat the recovered "source" as attacker-planted.
